from importlib import import_module
from typing import Dict, Optional, Tuple, Type

from app.config import settings
from app.notifications.providers.base import BaseNotificationProvider
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

PROVIDERS: Dict[str, Tuple[str, str]] = {
    "console": ("app.notifications.providers.console_provider", "ConsoleProvider"),
    "smtp": ("app.notifications.providers.smtp_provider", "SMTPProvider"),
    "resend": ("app.notifications.providers.resend_provider", "ResendProvider"),
    "sendgrid": ("app.notifications.providers.sendgrid_provider", "SendGridProvider"),
}


class NoOpProvider(BaseNotificationProvider):
    """Safely declines delivery when an optional provider is unavailable."""

    name = "noop"

    def __init__(self, provider_name: str, error: str):
        self.provider_name = provider_name
        self.error = error

    async def send_email(self, *args, **kwargs) -> Dict[str, Optional[str]]:
        return {
            "success": False,
            "provider": self.provider_name,
            "message_id": None,
            "error": self.error,
        }


def _get_provider_class(provider_name: str) -> Type[BaseNotificationProvider]:
    module_name, class_name = PROVIDERS[provider_name]
    module = import_module(module_name)
    return getattr(module, class_name)


def get_notification_provider(provider_name: Optional[str] = None) -> BaseNotificationProvider:
    """
    Factory function to retrieve the configured notification provider instance.
    """
    name = (provider_name or settings.EMAIL_PROVIDER or "console").lower().strip()
    if name not in PROVIDERS:
        name = "console"

    try:
        return _get_provider_class(name)()
    except (ImportError, AttributeError) as exc:
        error = f"Notification provider '{name}' is unavailable: {exc}"
        return NoOpProvider(name, error)
