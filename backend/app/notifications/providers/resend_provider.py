import asyncio
from typing import Optional, Dict, Any

try:
    import resend
except ImportError:
    resend = None

from app.config import settings
from app.notifications.providers.base import BaseNotificationProvider
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResendProvider(BaseNotificationProvider):
    name = "resend"

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        self.api_key = api_key or settings.RESEND_API_KEY
        self.from_email = from_email or settings.SMTP_FROM_EMAIL
        self.from_name = from_name or settings.SMTP_FROM_NAME
        if self.api_key and resend is not None:
            resend.api_key = self.api_key

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
            err = "Resend API key is not configured (RESEND_API_KEY)."
            logger.error(err)
            return {"success": False, "provider": self.name, "message_id": None, "error": err}

        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name
        full_sender = f"{sender_name} <{sender_email}>" if sender_name else sender_email

        params = {
            "from": full_sender,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }

        try:
            resp = resend.Emails.send(params)
            msg_id = getattr(resp, 'id', None) or (resp.get('id') if isinstance(resp, dict) else str(resp))
            logger.info(f"Resend email dispatched to {to_email} (MsgID: {msg_id})")
            return {
                "success": True,
                "provider": self.name,
                "message_id": msg_id,
                "error": None,
            }
        except Exception as e:
            err_msg = f"Resend request exception: {str(e)}"
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
        if resend is None:
            err = "Resend support is unavailable because the optional 'resend' package is not installed."
            return {"success": False, "provider": self.name, "message_id": None, "error": err}

        return await asyncio.to_thread(
            self._send_sync,
            to_email,
            subject,
            html_content,
            text_content,
            from_email,
            from_name,
        )
