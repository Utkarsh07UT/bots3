import uuid
from typing import Optional, Dict, Any
from app.notifications.providers.base import BaseNotificationProvider
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConsoleProvider(BaseNotificationProvider):
    """
    Console / Development Provider.
    Outputs formatted emails directly to server logs without needing an external mail server.
    """
    name = "console"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        msg_id = f"console-{uuid.uuid4().hex[:12]}"
        sender = f"{from_name or 'TheThirdEYE Alerts'} <{from_email or 'alerts@thethirdeye.sec'}>"

        logger.info(
            f"\n"
            f"+------------------------------------------------------------------------------+\n"
            f"| [MOCK / CONSOLE EMAIL DISPATCH]                                              |\n"
            f"+------------------------------------------------------------------------------+\n"
            f"| Message ID : {msg_id}\n"
            f"| From       : {sender}\n"
            f"| To         : {to_email}\n"
            f"| Subject    : {subject}\n"
            f"+------------------------------------------------------------------------------+\n"
            f"| [Body Preview - Text]:\n"
            f"| {text_content[:300].replace(chr(10), chr(10) + '| ')}...\n"
            f"+------------------------------------------------------------------------------+"
        )

        return {
            "success": True,
            "provider": self.name,
            "message_id": msg_id,
            "error": None,
        }
