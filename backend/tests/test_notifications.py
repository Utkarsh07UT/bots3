import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.db.models import NotificationPreference, NotificationLog, ThreatAlert
from app.notifications.rules import evaluate_notification_rules, is_in_quiet_hours
from app.notifications.rate_limiter import check_rate_limit
from app.notifications.providers import get_notification_provider, ConsoleProvider
from app.notifications.service import notification_service


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DummyAlert:
    def __init__(self, severity="HIGH", alert_id="alert-123", title="SYN Flood Detected"):
        self.alert_id = alert_id
        self.title = title
        self.description = "Suspicious volumetric surge in TCP SYN packets."
        self.severity = severity
        self.attack_type = "DDoS SYN Flood"
        self.source_ip = "192.168.1.100"
        self.target_ip = "10.0.0.1"
        self.target_port = 80
        self.confidence_score = 0.95
        self.contributing_bots = ["ddos_bot"]
        self.bot_scores = {"ddos_bot": 0.95}
        self.evidence = {"packet_rate_pps": 25000}
        self.blockchain_tx_hash = "0xabcdef1234567890"
        self.created_at = datetime.now(timezone.utc)


def test_severity_rules_default():
    crit_alert = DummyAlert(severity="CRITICAL")
    should_notify, reason = evaluate_notification_rules(crit_alert)
    assert should_notify is True
    assert reason == "ALLOWED"

    high_alert = DummyAlert(severity="HIGH")
    should_notify, reason = evaluate_notification_rules(high_alert)
    assert should_notify is True
    assert reason == "ALLOWED"

    low_alert = DummyAlert(severity="LOW")
    should_notify, reason = evaluate_notification_rules(low_alert)
    assert should_notify is False
    assert "SKIPPED" in reason


def test_preference_severity_filter():
    pref = NotificationPreference(
        email="test@thethirdeye.sec",
        is_enabled=True,
        min_severity="HIGH",
        notify_critical=True,
        notify_high=True,
        notify_medium=False,
        notify_low=False,
    )

    med_alert = DummyAlert(severity="MEDIUM")
    should_notify, reason = evaluate_notification_rules(med_alert, pref)
    assert should_notify is False

    high_alert = DummyAlert(severity="HIGH")
    should_notify, reason = evaluate_notification_rules(high_alert, pref)
    assert should_notify is True


def test_disabled_preference():
    pref = NotificationPreference(
        email="disabled@thethirdeye.sec",
        is_enabled=False,
    )
    crit_alert = DummyAlert(severity="CRITICAL")
    should_notify, reason = evaluate_notification_rules(crit_alert, pref)
    assert should_notify is False
    assert reason == "PREFERENCE_DISABLED"


def test_quiet_hours_logic():
    # 22:00 to 06:00 UTC
    assert is_in_quiet_hours(22, 6, 23) is True
    assert is_in_quiet_hours(22, 6, 2) is True
    assert is_in_quiet_hours(22, 6, 5) is True
    assert is_in_quiet_hours(22, 6, 6) is False
    assert is_in_quiet_hours(22, 6, 12) is False

    pref = NotificationPreference(
        email="quiet@thethirdeye.sec",
        is_enabled=True,
        quiet_hours_enabled=True,
        quiet_hours_start_utc=22,
        quiet_hours_end_utc=6,
    )

    midnight = datetime(2026, 8, 30, 2, 0, 0, tzinfo=timezone.utc)
    high_alert = DummyAlert(severity="HIGH")
    should_notify, reason = evaluate_notification_rules(high_alert, pref, current_time_utc=midnight)
    assert should_notify is False
    assert reason == "QUIET_HOURS_ACTIVE"

    # CRITICAL alert should override quiet hours
    crit_alert = DummyAlert(severity="CRITICAL")
    should_notify, reason = evaluate_notification_rules(crit_alert, pref, current_time_utc=midnight)
    assert should_notify is True
    assert "CRITICAL_OVERRIDE" in reason


def test_rate_limiter(db_session):
    test_email = f"ratelimit-{datetime.now().timestamp()}@thethirdeye.sec"

    # Initially allowed (0 sent)
    allowed, count = check_rate_limit(test_email, 3, db_session)
    assert allowed is True
    assert count == 0

    # Add 3 sent logs
    for i in range(3):
        log = NotificationLog(
            id=f"log-{datetime.now().timestamp()}-{i}",
            recipient=test_email,
            status="SUCCESS",
            sent_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
    db_session.commit()

    # Now should be rate limited at threshold of 3
    allowed, count = check_rate_limit(test_email, 3, db_session)
    assert allowed is False
    assert count == 3


def test_template_rendering():
    alert = DummyAlert(severity="CRITICAL", alert_id="alert-test-999")
    rendered = notification_service.render_templates(alert, "console")

    assert "[CRITICAL]" in rendered["subject"]
    assert "alert-test-999" in rendered["html"]
    assert "DDoS SYN Flood" in rendered["html"]
    assert "95.00%" in rendered["html"]
    assert "0xabcdef1234567890" in rendered["html"]

    # Plain text checks
    assert "alert-test-999" in rendered["text"]
    assert "DDoS SYN Flood" in rendered["text"]


def test_console_provider():
    provider = get_notification_provider("console")
    assert isinstance(provider, ConsoleProvider)

    res = asyncio.run(
        provider.send_email(
            to_email="analyst@thethirdeye.sec",
            subject="[TEST] Cyber Threat Alert",
            html_content="<p>Test</p>",
            text_content="Test",
        )
    )
    assert res["success"] is True
    assert res["provider"] == "console"
    assert res["message_id"] is not None


def test_send_test_notification():
    result = asyncio.run(
        notification_service.send_test_notification(
            to_email="test-analyst@thethirdeye.sec",
            provider_name="console",
            severity="CRITICAL",
        )
    )
    assert result["success"] is True
    assert result["provider"] == "console"
    assert "successfully" in result["message"]


def test_notifications_api_endpoints():
    client = TestClient(app)

    # 1. Create / Update Preference
    pref_payload = {
        "email": "soc-test-api@thethirdeye.sec",
        "name": "API Test Analyst",
        "is_enabled": True,
        "min_severity": "HIGH",
        "notify_critical": True,
        "notify_high": True,
        "notify_medium": False,
        "notify_low": False,
        "quiet_hours_enabled": True,
        "quiet_hours_start_utc": 23,
        "quiet_hours_end_utc": 5,
        "rate_limit_per_hour": 15,
    }
    create_res = client.post("/api/notifications/preferences", json=pref_payload)
    assert create_res.status_code in (200, 201)
    data = create_res.json()
    assert data["email"] == "soc-test-api@thethirdeye.sec"
    assert data["rate_limit_per_hour"] == 15

    # 2. List Preferences
    list_res = client.get("/api/notifications/preferences")
    assert list_res.status_code == 200
    prefs = list_res.json()
    assert any(p["email"] == "soc-test-api@thethirdeye.sec" for p in prefs)

    # 3. Send Test Email via API
    test_req = {
        "email": "soc-test-api@thethirdeye.sec",
        "provider": "console",
        "severity": "CRITICAL",
    }
    test_res = client.post("/api/notifications/test", json=test_req)
    assert test_res.status_code == 200
    test_data = test_res.json()
    assert test_data["success"] is True

    # 4. View Logs
    logs_res = client.get("/api/notifications/logs?limit=10")
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) > 0
