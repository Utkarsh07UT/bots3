import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

MOCK_ALERTS = [
    {
        "id": "1",
        "timestamp": "2026-08-25T14:30:00Z",
        "flow_id": "src:1.2.3.4-dst:5.6.7.8-proto:TCP",
        "threat_class": "syn_flood",
        "confidence": 0.93,
        "severity": "high",
        "evidence": {"syn_rate": 45000, "src_entropy": 0.11},
        "blockchain_tx": "0xabc..."
    },
    {
        "id": "2",
        "timestamp": "2026-08-25T14:32:00Z",
        "flow_id": "src:9.9.9.9-dst:8.8.8.8-proto:UDP",
        "threat_class": "port_scan",
        "confidence": 0.81,
        "severity": "medium",
        "evidence": {"unique_ports": 340},
        "blockchain_tx": "0xdef..."
    }
]


def _normalise(alert: dict[str, Any]) -> dict[str, Any]:
    """Accept the demo detector format while preserving the legacy API shape."""
    if "id" in alert:
        return alert
    return {
        "id": alert.get("alert_id"),
        "timestamp": alert.get("observed_at"),
        "flow_id": f"{alert.get('source_host', '-')}-{alert.get('destination_host', '-')}",
        "threat_class": alert.get("threat_type"),
        "confidence": alert.get("confidence", 0),
        "severity": alert.get("severity", "low"),
        "evidence": {"reasons": alert.get("reasons", []), "signals": alert.get("signals", [])},
        **alert,
    }


def import_alerts(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Alert import must be a JSON array")
    MOCK_ALERTS[:] = [_normalise(item) for item in payload]
    return len(MOCK_ALERTS)


configured_demo = os.getenv("DEMO_ALERTS_PATH")
if configured_demo:
    demo_path = Path(configured_demo)
    if demo_path.is_file():
        import_alerts(demo_path)

@router.get("/alerts")
def get_alerts():
    return MOCK_ALERTS

@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str):
    alert = next((a for a in MOCK_ALERTS if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/import")
def import_alerts_endpoint(payload: list[dict[str, Any]]):
    """Replace the in-memory demo feed with detector-exported alerts."""
    MOCK_ALERTS[:] = [_normalise(item) for item in payload]
    return {"imported": len(MOCK_ALERTS)}
