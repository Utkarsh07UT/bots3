import os
import asyncio
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import SessionLocal
from app.db.models import ThreatAlert, NotificationPreference, NotificationLog
from app.notifications.providers import get_notification_provider
from app.notifications.rules import evaluate_notification_rules
from app.notifications.rate_limiter import check_rate_limit
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


class NotificationService:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_templates(self, alert_data: Any, provider_name: str) -> Dict[str, str]:
        """
        Renders HTML and plain-text email templates for a threat alert.
        """
        if isinstance(alert_data, dict):
            alert_id = alert_data.get("alert_id", "")
            severity = alert_data.get("severity", "MEDIUM")
            title = alert_data.get("title", "Threat Alert")
            created_at = alert_data.get("created_at")
        else:
            alert_id = getattr(alert_data, "alert_id", "")
            severity = getattr(alert_data, "severity", "MEDIUM")
            title = getattr(alert_data, "title", "Threat Alert")
            created_at = getattr(alert_data, "created_at", None)

        if isinstance(created_at, datetime):
            timestamp_utc = created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        frontend_url = settings.FRONTEND_BASE_URL.rstrip("/")
        incident_url = f"{frontend_url}/dashboard"
        if alert_id:
            incident_url = f"{frontend_url}/dashboard?alert_id={alert_id}"

        context = {
            "alert": alert_data,
            "incident_url": incident_url,
            "frontend_url": frontend_url,
            "timestamp_utc": timestamp_utc,
            "provider_name": provider_name.upper(),
        }

        html_template = self.jinja_env.get_template("alert_email.html")
        text_template = self.jinja_env.get_template("alert_email.txt")

        subject = f"[{severity.upper()}] Threat Alert: {title} | TheThirdEYE SOC"

        return {
            "subject": subject,
            "html": html_template.render(context),
            "text": text_template.render(context),
        }

    async def _send_with_retry(
        self,
        provider,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Executes email dispatch with exponential backoff for transient failures.
        """
        attempt = 0
        last_result = None

        while attempt < max_retries:
            attempt += 1
            result = await provider.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
            last_result = result
            if result.get("success"):
                result["retry_count"] = attempt - 1
                return result

            # Transient failure backoff: 1s, 2s, 4s...
            if attempt < max_retries:
                backoff = 2 ** (attempt - 1)
                logger.warning(
                    f"Notification to {to_email} failed (attempt {attempt}/{max_retries}). Retrying in {backoff}s... Error: {result.get('error')}"
                )
                await asyncio.sleep(backoff)

        if last_result:
            last_result["retry_count"] = attempt - 1
        return last_result or {"success": False, "error": "Unknown dispatch error", "retry_count": attempt}

    def _get_target_recipients(self, db: Session) -> List[Dict[str, Any]]:
        """
        Retrieves active recipients from preferences, or falls back to configured default emails.
        """
        try:
            prefs = db.query(NotificationPreference).filter(NotificationPreference.is_enabled == True).all()
            if prefs:
                return [{"email": p.email, "preference": p} for p in prefs]
        except Exception as e:
            logger.error(f"Failed to query notification preferences from DB: {e}")

        # Fallback to configured environment defaults
        return [{"email": email, "preference": None} for email in settings.DEFAULT_ALERT_EMAILS if email]

    async def process_alert_notifications(
        self,
        alert: Any,
        provider_name: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> List[NotificationLog]:
        """
        Processes and dispatches notifications for a ThreatAlert across all configured recipients.
        """
        if not settings.EMAIL_NOTIFICATIONS_ENABLED:
            logger.info("Email notifications are globally disabled (EMAIL_NOTIFICATIONS_ENABLED=false).")
            return []

        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True

        provider = get_notification_provider(provider_name)
        rendered = self.render_templates(alert, provider.name)
        logs: List[NotificationLog] = []

        try:
            recipients = self._get_target_recipients(db)
            alert_id = getattr(alert, "alert_id", None) or (alert.get("alert_id") if isinstance(alert, dict) else None)

            for target in recipients:
                to_email = target["email"]
                pref = target.get("preference")
                rate_limit = pref.rate_limit_per_hour if pref else settings.NOTIFICATION_RATE_LIMIT_PER_HOUR

                # 1. Evaluate severity & quiet hours rules
                should_notify, rule_reason = evaluate_notification_rules(alert, pref)
                if not should_notify:
                    log_entry = NotificationLog(
                        id=str(uuid.uuid4()),
                        alert_id=alert_id,
                        recipient=to_email,
                        channel="email",
                        provider=provider.name,
                        status="SKIPPED" if "SKIPPED" in rule_reason or "DISABLED" in rule_reason else "QUIET_HOURS",
                        subject=rendered["subject"],
                        error_message=f"Suppressed by policy: {rule_reason}",
                        retry_count=0,
                        sent_at=datetime.now(timezone.utc),
                    )
                    db.add(log_entry)
                    logs.append(log_entry)
                    continue

                # 2. Rate limiting check
                is_allowed, count = check_rate_limit(to_email, rate_limit, db)
                if not is_allowed:
                    log_entry = NotificationLog(
                        id=str(uuid.uuid4()),
                        alert_id=alert_id,
                        recipient=to_email,
                        channel="email",
                        provider=provider.name,
                        status="RATE_LIMITED",
                        subject=rendered["subject"],
                        error_message=f"Rate limit exceeded: {count}/{rate_limit} in last hour",
                        retry_count=0,
                        sent_at=datetime.now(timezone.utc),
                    )
                    db.add(log_entry)
                    logs.append(log_entry)
                    continue

                # 3. Dispatch email with retry
                send_res = await self._send_with_retry(
                    provider=provider,
                    to_email=to_email,
                    subject=rendered["subject"],
                    html_content=rendered["html"],
                    text_content=rendered["text"],
                    max_retries=settings.NOTIFICATION_RETRY_ATTEMPTS,
                )

                status = "SUCCESS" if send_res.get("success") else "FAILED"
                error_msg = send_res.get("error")

                log_entry = NotificationLog(
                    id=str(uuid.uuid4()),
                    alert_id=alert_id,
                    recipient=to_email,
                    channel="email",
                    provider=provider.name,
                    status=status,
                    subject=rendered["subject"],
                    error_message=error_msg,
                    retry_count=send_res.get("retry_count", 0),
                    sent_at=datetime.now(timezone.utc),
                )
                db.add(log_entry)
                logs.append(log_entry)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error in process_alert_notifications: {e}", exc_info=True)
        finally:
            if own_db:
                db.close()

        return logs

    def notify_alert_sync(
        self,
        alert: Any,
        provider_name: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> List[NotificationLog]:
        """
        Synchronous wrapper around process_alert_notifications.
        """
        return asyncio.run(self.process_alert_notifications(alert, provider_name, db))

    def notify_alert_background(self, alert: Any, provider_name: Optional[str] = None) -> None:
        """
        Non-blocking fire-and-forget background dispatcher.
        Ensures main controller and flow processing never wait for email delivery.
        """
        alert_id = getattr(alert, "alert_id", None) or (alert.get("alert_id") if isinstance(alert, dict) else None)
        
        def _run():
            try:
                db = SessionLocal()
                try:
                    from app.db.models import ThreatAlert
                    db_alert = db.query(ThreatAlert).filter(ThreatAlert.alert_id == alert_id).first()
                    target_alert = db_alert if db_alert else alert
                    asyncio.run(self.process_alert_notifications(target_alert, provider_name, db))
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Background notification thread error: {e}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    async def send_test_notification(
        self,
        to_email: str,
        provider_name: Optional[str] = None,
        severity: str = "HIGH",
    ) -> Dict[str, Any]:
        """
        Sends an immediate simulated test notification to verify provider setup.
        """
        provider = get_notification_provider(provider_name)
        simulated_alert = {
            "alert_id": f"test-{uuid.uuid4().hex[:8]}",
            "title": f"Simulated {severity} Threat Alert (Test Dispatch)",
            "description": "This is a verified test alert dispatched from TheThirdEYE Cyber Threat Operations Center.",
            "severity": severity.upper(),
            "attack_type": "SYN_FLOOD_SIMULATION",
            "source_ip": "198.51.100.42",
            "target_ip": "10.0.4.15",
            "target_port": 443,
            "confidence_score": 0.9850,
            "contributing_bots": ["ddos_bot", "beaconing_bot"],
            "bot_scores": {"ddos_bot": 0.992, "beaconing_bot": 0.945},
            "evidence": {
                "flow_rate_bps": 48500000.0,
                "packet_rate_pps": 32400.0,
                "protocol": "TCP",
                "tcp_flags": "SYN",
                "duration": 0.045,
            },
            "blockchain_tx_hash": "0x4a8f9c1b3e7d2a5f6e8c0b1d3f5a7e9c2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a",
        }

        rendered = self.render_templates(simulated_alert, provider.name)
        send_res = await self._send_with_retry(
            provider=provider,
            to_email=to_email,
            subject=f"[TEST] {rendered['subject']}",
            html_content=rendered["html"],
            text_content=rendered["text"],
        )

        db = SessionLocal()
        try:
            log_entry = NotificationLog(
                id=str(uuid.uuid4()),
                alert_id=simulated_alert["alert_id"],
                recipient=to_email,
                channel="email",
                provider=provider.name,
                status="SUCCESS" if send_res.get("success") else "FAILED",
                subject=f"[TEST] {rendered['subject']}",
                error_message=send_res.get("error"),
                retry_count=send_res.get("retry_count", 0),
                sent_at=datetime.now(timezone.utc),
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log test notification: {e}")
        finally:
            db.close()

        return {
            "success": send_res.get("success", False),
            "provider": provider.name,
            "recipient": to_email,
            "message": "Test email sent successfully" if send_res.get("success") else f"Dispatch failed: {send_res.get('error')}",
            "details": send_res,
        }


notification_service = NotificationService()
