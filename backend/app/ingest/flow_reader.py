"""
1. Receive Traffic -> 2. Feature Extractor -> 3. Send to AI Bots -> 4. Redis Event Bus
"""
import time
import uuid
import random
import requests
import json
import os
from app.streaming.redis_client import get_redis_client

r = get_redis_client()
STREAM_NAME = "bot:predictions"
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://bots3-a8ta.onrender.com")
ACTIVE_BOTS = ["ddos_bot", "beaconing_bot", "dga_dns_bot", "encrypted_malware_bot", "exfiltration_bot"]

def generate_mock_flow():
    is_malicious = random.random() < 0.3
    if is_malicious:
        return {
            "flow_id": str(uuid.uuid4()),
            "src_ip": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
            "dst_ip": "10.0.0.5",
            "src_port": str(random.randint(1024, 65535)),
            "dst_port": str(random.choice([80, 443, 22, 3389, 53])),
            "protocol": "TCP",
            "packet_count": str(random.randint(5000, 50000)),
            "byte_count": str(random.randint(1000000, 50000000)),
            "duration_ms": str(random.randint(10, 5000))
        }
    else:
        return {
            "flow_id": str(uuid.uuid4()),
            "src_ip": f"192.168.1.{random.randint(2, 254)}",
            "dst_ip": f"10.0.0.{random.randint(2, 254)}",
            "src_port": str(random.randint(1024, 65535)),
            "dst_port": str(random.choice([80, 443, 8080])),
            "protocol": "TCP",
            "packet_count": str(random.randint(1, 50)),
            "byte_count": str(random.randint(100, 5000)),
            "duration_ms": str(random.randint(10, 500))
        }

def start_ingestion(count=10, delay=1.0):
    print(f"[INGEST] Started pipeline. Target Redis: {STREAM_NAME}")
    for i in range(count):
        flow = generate_mock_flow()
        
        bot_payload = {
            "duration": float(flow.get("duration_ms", 0)) / 1000.0,
            "packet_count": int(flow.get("packet_count", 0)),
            "byte_count": int(flow.get("byte_count", 0)),
            "protocol": flow.get("protocol", "TCP"),
            "src_ip": flow.get("src_ip", "0.0.0.0"),
            "dst_ip": flow.get("dst_ip", "0.0.0.0"),
        }
        
        predictions = {}
        for bot in ACTIVE_BOTS:
            try:
                resp = requests.post(f"{AI_SERVICE_URL}/predict/{bot}", json=bot_payload, timeout=5)
                if resp.status_code == 200:
                    predictions[bot] = resp.json()
            except Exception as e:
                print(f"[INGEST] Bot {bot} failed: {e}")
        
        # Package flow + predictions -> Redis
        event_data = {
            "flow": json.dumps(flow),
            "predictions": json.dumps(predictions)
        }
        
        r.xadd(STREAM_NAME, event_data)
        print(f"[INGEST] Extracted features -> Sent to {len(predictions)} Bots -> Pushed to Redis sliding window.")
        time.sleep(delay)

if __name__ == "__main__":
    start_ingestion(count=1000, delay=2.0)
