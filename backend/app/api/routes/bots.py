from fastapi import APIRouter
import time

router = APIRouter()

MOCK_BOT_HEALTH = [
    {"bot_name": "ddos_bot", "status": "healthy", "last_active": time.time(), "throughput": 1200},
    {"bot_name": "beaconing_bot", "status": "healthy", "last_active": time.time(), "throughput": 850},
    {"bot_name": "dga_dns_bot", "status": "degraded", "last_active": time.time() - 30, "throughput": 200},
    {"bot_name": "encrypted_malware_bot", "status": "healthy", "last_active": time.time(), "throughput": 640},
    {"bot_name": "scanning_bot", "status": "healthy", "last_active": time.time(), "throughput": 1100},
    {"bot_name": "exfiltration_bot", "status": "offline", "last_active": time.time() - 300, "throughput": 0},
]

@router.get("/bots/health")
def get_bot_health():
    return MOCK_BOT_HEALTH