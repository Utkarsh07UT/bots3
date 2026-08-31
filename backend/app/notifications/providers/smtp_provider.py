import smtplib
import ssl
import asyncio
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any

from app.config import settings
from app.notifications.providers.base import BaseNotificationProvider
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SMTPProvider(BaseNotificationProvider):
    name = "smtp"

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.username = username or settings.SMTP_USER
        self.password = password or settings.SMTP_PASSWORD
        self.use_tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS
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
        msg_id = f"smtp-{uuid.uuid4().hex[:12]}"
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name
        full_sender = f"{sender_name} <{sender_email}>" if sender_name else sender_email

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = full_sender
        message["To"] = to_email
        message["Message-ID"] = f"<{msg_id}@{self.host}>"

        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        message.attach(part1)
        message.attach(part2)

        try:
            # Port 465 is typically SSL, 587 or 25 is typically STARTTLS
            if self.port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=15) as server:
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(sender_email, [to_email], message.as_string())
            else:
                with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                    server.ehlo()
                    if self.use_tls:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                        server.ehlo()
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(sender_email, [to_email], message.as_string())

            logger.info(f"SMTP email sent to {to_email} (MsgID: {msg_id})")
            return {
                "success": True,
                "provider": self.name,
                "message_id": msg_id,
                "error": None,
            }
        except Exception as e:
            err_msg = f"SMTP transmission error to {to_email}: {str(e)}"
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
