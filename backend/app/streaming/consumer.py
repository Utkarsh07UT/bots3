import os
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from app.streaming.redis_client import get_redis_client
from app.db.session import SessionLocal
from app.db.models import NetworkFlow
from app.controller.main_controller import evaluate_flow_fusion

STREAM_NAME = "bot:predictions"
GROUP_NAME = "score_fusion_consumers"
CONSUMER_NAME = "fusion_node_1"

r = get_redis_client()

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"consumer alive")
    def log_message(self, format, *args): pass

def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

def ensure_group():
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise

def process_event(event_id: str, data: dict, db):
    raw_flow_str = data.get("flow") or data.get(b"flow") or "{}"
    if isinstance(raw_flow_str, bytes): raw_flow_str = raw_flow_str.decode("utf-8")
    raw_flow = json.loads(raw_flow_str)
    
    pred_str = data.get("predictions") or data.get(b"predictions") or "{}"
    if isinstance(pred_str, bytes): pred_str = pred_str.decode("utf-8")
    predictions = json.loads(pred_str)
    
    flow_db = NetworkFlow(
        flow_id=raw_flow.get("flow_id"),
        src_ip=raw_flow.get("src_ip"),
        dst_ip=raw_flow.get("dst_ip"),
        src_port=int(raw_flow.get("src_port", 0)),
        dst_port=int(raw_flow.get("dst_port", 0)),
        protocol=raw_flow.get("protocol", "TCP"),
        pkts_in=int(raw_flow.get("packet_count", 0)),
        bytes_in=int(raw_flow.get("byte_count", 0)),
        duration=float(raw_flow.get("duration_ms", 0)) / 1000.0,
    )
    db.add(flow_db)
    
    # 5. Main Controller (Score Fusion)
    evaluate_flow_fusion(raw_flow, predictions, db)
    
    db.commit()
    r.xack(STREAM_NAME, GROUP_NAME, event_id)

def run_consumer():
    ensure_group()
    print(f"Listening on stream '{STREAM_NAME}'...")
    db = SessionLocal()
    try:
        while True:
            try:
                entries = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME: ">"}, count=10, block=5000)
            except Exception as e:
                time.sleep(2)
                continue

            if not entries: continue

            for _, events in entries:
                for event_id, data in events:
                    try:
                        process_event(event_id, data, db)
                    except Exception as e:
                        print(f"Error processing {event_id}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    threading.Thread(target=start_dummy_server, daemon=True).start()
    run_consumer()
