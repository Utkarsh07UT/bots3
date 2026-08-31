from datetime import datetime, timezone
from typing import Optional, Tuple, Any

from app.db.models import NotificationPreference


SEVERITY_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def is_in_quiet_hours(start_hour_utc: int, end_hour_utc: int, current_hour_utc: int) -> bool:
    """
    Checks if current UTC hour falls within the quiet hours window.
    Handles overnight rollover (e.g., 22:00 to 06:00 UTC).
    """
    if start_hour_utc <= end_hour_utc:
        return start_hour_utc <= current_hour_utc < end_hour_utc
    else:
        # Crosses midnight: e.g. start=22, end=6 -> True if >= 22 or < 6
        return current_hour_utc >= start_hour_utc or current_hour_utc < end_hour_utc


def evaluate_notification_rules(
    alert: Any,
    preference: Optional[NotificationPreference] = None,
    current_time_utc: Optional[datetime] = None,
) -> Tuple[bool, str]:
    """
    Evaluates whether an email notification should be dispatched for an alert
    based on severity policies and recipient preferences.

    Returns:
        (should_notify: bool, reason: str)
    """
    now = current_time_utc or datetime.now(timezone.utc)
    current_hour = now.hour
    severity = getattr(alert, "severity", "MEDIUM").upper()

    # 1. Master enable/disable
    if preference is not None and not preference.is_enabled:
        return False, "PREFERENCE_DISABLED"

    # 2. Severity-based rules
    if preference is not None:
        min_sev_str = (preference.min_severity or "MEDIUM").upper()
        min_sev_score = SEVERITY_LEVELS.get(min_sev_str, 2)
        alert_sev_score = SEVERITY_LEVELS.get(severity, 2)

        if alert_sev_score < min_sev_score:
            return False, f"BELOW_MIN_SEVERITY_{min_sev_str}"

        if severity == "CRITICAL" and preference.notify_critical is False:
            return False, "CRITICAL_DISABLED_BY_USER"
        if severity == "HIGH" and preference.notify_high is False:
            return False, "HIGH_DISABLED_BY_USER"
        if severity == "MEDIUM" and preference.notify_medium is False:
            return False, "MEDIUM_DISABLED_BY_USER"
        if severity == "LOW" and not bool(preference.notify_low):
            return False, "LOW_DISABLED_BY_USER"
    else:
        # Default global policy when no custom preference record exists
        if severity == "LOW":
            return False, "LOW_SEVERITY_SKIPPED_BY_DEFAULT"

    # 3. Quiet Hours Check
    if preference is not None and preference.quiet_hours_enabled:
        if is_in_quiet_hours(preference.quiet_hours_start_utc, preference.quiet_hours_end_utc, current_hour):
            # Critical alerts override quiet hours for emergency SOC awareness
            if severity == "CRITICAL":
                return True, "CRITICAL_OVERRIDE_QUIET_HOURS"
            return False, "QUIET_HOURS_ACTIVE"

    return True, "ALLOWED"
