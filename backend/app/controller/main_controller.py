"""
Main Controller AI — calls each specialist bot's /predict endpoint,
and if a bot flags malicious traffic, writes a ThreatAlert.
"""
import requests
import uuid
from app.db.session import SessionLocal
from app.db.models import ThreatAlert

import os
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://three-1-1oz2.onrender.com")
CONFIDENCE_THRESHOLD = 0.7

# Bots currently known to work; add scanning_bot once fixed
ACTIVE_BOTS = [
    "ddos_bot",
    "beaconing_bot",
    "dga_dns_bot",
    "encrypted_malware_bot",
    "exfiltration_bot",
]


def call_bot(bot_name: str, payload: dict) -> dict:
    resp = requests.post(
        f"{AI_SERVICE_URL}/predict/{bot_name}",
        json=payload,
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()


def evaluate_flow(flow_data: dict, bot_name: str, bot_payload: dict):
    """
    Calls one bot with the given payload. If malicious, writes an alert.
    """
    try:
        result = call_bot(bot_name, bot_payload)
    except Exception as e:
        print(f"{bot_name}: call failed - {e}")
        return None

    if result.get("malicious") and result.get("confidence", 0) >= CONFIDENCE_THRESHOLD:
        db = SessionLocal()
        try:
            alert = ThreatAlert(
                alert_id=str(uuid.uuid4()),
                title=f"{result.get('category', bot_name)} detected",
                description=f"{bot_name} flagged traffic as {result.get('label')}",
                severity=result.get("severity", "MEDIUM").upper(),
                attack_type=result.get("label", "unknown"),
                source_ip=flow_data.get("src_ip", "unknown"),
                target_ip=flow_data.get("dst_ip", "unknown"),
                confidence_score=result.get("confidence", 0.0),
                contributing_bots=[bot_name],
                bot_scores={bot_name: result.get("confidence", 0.0)},
                evidence=result.get("features", {}),
            )
            db.add(alert)
            db.commit()
            print(f"ALERT created: {alert.alert_id} ({bot_name}, {result.get('confidence')})")
            return alert
        finally:
            db.close()
    else:
        print(f"{bot_name}: benign/low-confidence ({result.get('confidence')}), no alert")
        return None