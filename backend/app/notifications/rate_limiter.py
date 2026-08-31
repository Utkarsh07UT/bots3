from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.db.models import NotificationLog
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def check_rate_limit(
    recipient: str,
    limit_per_hour: int,
    db: Session,
    current_time_utc: Optional[datetime] = None,
) -> Tuple[bool, int]:
    """
    Checks if a recipient has exceeded their allowable notifications in the last 60 minutes.

    Returns:
        (is_allowed: bool, recent_count: int)
    """
    now = current_time_utc or datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    try:
        count = (
            db.query(NotificationLog)
            .filter(
                NotificationLog.recipient == recipient,
                NotificationLog.status == "SUCCESS",
                NotificationLog.sent_at >= one_hour_ago,
            )
            .count()
        )

        if count >= limit_per_hour:
            logger.warning(
                f"Rate limit exceeded for recipient '{recipient}': {count}/{limit_per_hour} emails sent in last hour."
            )
            return False, count

        return True, count
    except Exception as e:
        logger.error(f"Error checking rate limit for {recipient}: {e}")
        # In case of DB error checking rate limits, allow sending so critical alerts are not dropped
        return True, 0
