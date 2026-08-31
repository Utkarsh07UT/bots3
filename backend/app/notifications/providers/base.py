from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseNotificationProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends an email message to the specified recipient.

        Returns a dictionary:
        {
            "success": bool,
            "provider": str,
            "message_id": Optional[str],
            "error": Optional[str]
        }
        """
        pass
