import asyncio
import requests
from typing import Optional, Dict, Any

from app.config import settings
from app.notifications.providers.base import BaseNotificationProvider
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SendGridProvider(BaseNotificationProvider):
    name = "sendgrid"
    API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        self.api_key = api_key or settings.SENDGRID_API_KEY
        self.from_email = from_email or settings.SMTP_FROM_EMAIL
        self.from_name = from_name or settings.SMTP_FROM_NAME

    def _send_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            err = "SendGrid API key is not configured (SENDGRID_API_KEY)."
            logger.error(err)
            return {"success": False, "provider": self.name, "message_id": None, "error": err}

        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name

        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": sender_email, "name": sender_name},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_content},
                {"type": "text/html", "value": html_content},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TheThirdEYE-SOC/1.0",
        }

        try:
            resp = requests.post(self.API_URL, json=payload, headers=headers, timeout=15)
            # SendGrid returns 202 Accepted on success
            if resp.status_code in (200, 201, 202):
                msg_id = resp.headers.get("X-Message-Id", "sg-accepted")
                logger.info(f"SendGrid email dispatched to {to_email} (MsgID: {msg_id})")
                return {
                    "success": True,
                    "provider": self.name,
                    "message_id": msg_id,
                    "error": None,
                }
            else:
                err_msg = f"SendGrid API error ({resp.status_code}): {resp.text}"
                logger.error(err_msg)
                return {
                    "success": False,
                    "provider": self.name,
                    "message_id": None,
                    "error": err_msg,
                }
        except Exception as e:
            err_msg = f"SendGrid request exception: {str(e)}"
            logger.error(err_msg)
            return {
                "success": False,
                "provider": self.name,
                "message_id": None,
                "error": err_msg,
            }

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            self._send_sync,
            to_email,
            subject,
            html_content,
            text_content,
            from_email,
            from_name,
        )
