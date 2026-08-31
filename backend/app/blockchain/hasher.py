import hashlib
import json
from typing import Any, Dict

def hash_alert(alert_data: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash of a ThreatAlert dictionary.
    Keys are sorted to ensure reproducibility.
    """
    # Remove mutable or system-generated fields that might not be identical across runs/DB saves
    # e.g., 'created_at', 'updated_at', 'id', 'status' might change. We hash the core alert content.
    core_fields = {
        "alert_id": alert_data.get("alert_id"),
        "title": alert_data.get("title"),
        "severity": alert_data.get("severity"),
        "attack_type": alert_data.get("attack_type"),
        "source_ip": alert_data.get("source_ip"),
        "target_ip": alert_data.get("target_ip"),
        "confidence_score": float(alert_data.get("confidence_score", 0.0)),
    }
    
    # Serialize to JSON with sorted keys
    serialized = json.dumps(core_fields, sort_keys=True, separators=(',', ':'))
    
    # Generate SHA-256 hash
    return "0x" + hashlib.sha256(serialized.encode('utf-8')).hexdigest()
