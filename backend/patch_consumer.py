import re

with open("backend/app/streaming/consumer.py", "r") as f:
    content = f.read()

# Add import for evaluate_flow_fusion
content = content.replace(
    'from app.db.models import NetworkFlow',
    'from app.db.models import NetworkFlow\nfrom app.controller.main_controller import evaluate_flow_fusion'
)

# Update process_event to call it
new_process_event = '''
def process_event(event_id: str, data: dict, db):
    flow_dict = {
        "flow_id": data.get("flow_id"),
        "src_ip": data.get("src_ip"),
        "dst_ip": data.get("dst_ip"),
        "src_port": int(data.get("src_port", 0)),
        "dst_port": int(data.get("dst_port", 0)),
        "protocol": data.get("protocol", "TCP"),
        "pkts_in": int(data.get("packet_count", 0)),
        "bytes_in": int(data.get("byte_count", 0)),
        "duration": float(data.get("duration_ms", 0)) / 1000.0,
    }
    
    flow = NetworkFlow(**flow_dict)
    db.add(flow)
    
    # 5. Main Controller (Score Fusion)
    evaluate_flow_fusion(flow_dict, db)
    
    db.commit()
    r.xack(STREAM_NAME, GROUP_NAME, event_id)
'''

# Use regex to replace the process_event function
pattern = re.compile(r'def process_event.*?r\.xack\(STREAM_NAME, GROUP_NAME, event_id\)', re.DOTALL)
content = pattern.sub(new_process_event.strip(), content)

with open("backend/app/streaming/consumer.py", "w") as f:
    f.write(content)
