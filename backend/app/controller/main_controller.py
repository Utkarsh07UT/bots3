"""
Main Controller AI — Score Fusion.
Consumes predictions from Redis Event Bus, fuses their scores,
and if a threshold is crossed, generates a ThreatAlert.
"""
import os
import uuid
import requests
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models import ThreatAlert
from app.notifications.service import notification_service

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://bots3-a8ta.onrender.com")
CONFIDENCE_THRESHOLD = 0.65

# All 6 specialist bots active for multi-bot threat detection
ACTIVE_BOTS = [
    "ddos_bot",
    "beaconing_bot",
    "dga_dns_bot",
    "encrypted_malware_bot",
    "scanning_bot",
    "exfiltration_bot",
]


def call_bot(bot_name: str, payload: dict) -> dict:
    resp = requests.post(
        f"{AI_SERVICE_URL}/predict/{bot_name}",
        json=payload,
        timeout=60
    )
    resp.raise_for_status()
    return resp.json()


def log_to_blockchain(alert_id: str, attack_label: str, confidence: float) -> str:
    """
    Log alert to blockchain and return transaction hash.
    """
    # Placeholder implementation - replace with actual blockchain integration
    return f"0x{uuid.uuid4().hex[:64]}"


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
            notification_service.notify_alert_background(alert)
            return alert
        finally:
            db.close()
    else:
        print(f"{bot_name}: benign/low-confidence ({result.get('confidence')}), no alert")
        return None


def evaluate_flow_fusion(flow_data: dict, bot_predictions: dict, db):
    """
    Score Fusion logic based on the bot predictions retrieved from Redis Event Bus.
    """
    total_confidence = 0.0
    malicious_votes = 0

    for bot, res in bot_predictions.items():
        if res.get("malicious"):
            malicious_votes += 1
            total_confidence += res.get("confidence", 0.0)

    # 5. Main Controller (Score Fusion)
    if malicious_votes > 0:
        fused_confidence = total_confidence / malicious_votes
        
        # Boost confidence if multiple bots detected it
        if malicious_votes > 1:
            fused_confidence = min(0.99, fused_confidence + (malicious_votes * 0.05))

        if fused_confidence >= CONFIDENCE_THRESHOLD:
            # Determine primary attack type (only from bots that predicted malicious)
            malicious_preds = {k: v for k, v in bot_predictions.items() if v.get("malicious")}
            primary_bot = max(malicious_preds.items(), key=lambda x: x[1].get("confidence", 0))[0]
            primary_res = malicious_preds[primary_bot]
            
            actual_attack_type = flow_data.get("attack_type", "BENIGN")
            display_attack_type = actual_attack_type if actual_attack_type != "BENIGN" else primary_res.get("label", "Unknown")
            display_title = actual_attack_type.replace('_', ' ').title() if actual_attack_type != "BENIGN" else primary_res.get("category", primary_bot).replace('_', ' ').title()

            alert_id = str(uuid.uuid4())
            
            # 6. Log to Blockchain
            tx_hash = log_to_blockchain(alert_id, display_attack_type, fused_confidence)

            # 7. Save Alert in PostgreSQL
            alert = ThreatAlert(
                alert_id=alert_id,
                title=f"{display_title} Detected",
                description=f"Score Fusion engine detected malicious activity flagged by {malicious_votes} specialist bots.",
                severity="CRITICAL" if fused_confidence > 0.85 else "HIGH",
                attack_type=display_attack_type,
                source_ip=flow_data.get("src_ip", "unknown"),
                target_ip=flow_data.get("dst_ip", "unknown"),
                confidence_score=fused_confidence,
                contributing_bots=[b for b, res in bot_predictions.items() if res.get("malicious")],
                bot_scores={b: res.get("confidence", 0) for b, res in bot_predictions.items()},
                evidence={"tx_hash": tx_hash, "fused_confidence": fused_confidence}
            )
            db.add(alert)
            print(f"[FUSION] ALERT created: {alert.alert_id} (Type: {display_attack_type})")
            notification_service.notify_alert_background(alert)
            return alert
    
    # If benign (no malicious votes, or below threshold)
    alert = ThreatAlert(
        alert_id=str(uuid.uuid4()),
        title="Normal Traffic",
        description="All bots classified traffic as benign.",
        severity="LOW",
        attack_type="BENIGN",
        source_ip=flow_data.get("src_ip", "unknown"),
        target_ip=flow_data.get("dst_ip", "unknown"),
        confidence_score=1.0,
        status="RESOLVED",
        contributing_bots=[],
        bot_scores={b: res.get("confidence", 0) for b, res in bot_predictions.items()},
        evidence={}
    )
    db.add(alert)
    print(f"[FUSION] BENIGN traffic logged: {alert.alert_id}")
    return alert
