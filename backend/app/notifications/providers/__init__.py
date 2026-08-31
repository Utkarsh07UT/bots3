from typing import Optional, Dict, Type

from app.config import settings
from app.notifications.providers.base import BaseNotificationProvider
from app.notifications.providers.console_provider import ConsoleProvider
from app.notifications.providers.smtp_provider import SMTPProvider
from app.notifications.providers.resend_provider import ResendProvider
from app.notifications.providers.sendgrid_provider import SendGridProvider

PROVIDERS: Dict[str, Type[BaseNotificationProvider]] = {
    "console": ConsoleProvider,
    "smtp": SMTPProvider,
    "resend": ResendProvider,
    "sendgrid": SendGridProvider,
}


def get_notification_provider(provider_name: Optional[str] = None) -> BaseNotificationProvider:
    """
    Factory function to retrieve the configured notification provider instance.
    """
    name = (provider_name or settings.EMAIL_PROVIDER or "console").lower().strip()
    provider_cls = PROVIDERS.get(name, ConsoleProvider)
    return provider_cls()
