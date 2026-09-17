import os
import json
import uuid
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone

with open("frontend/.env", "r") as f:
    env_content = f.read()

supabase_url = ""
supabase_key = ""
for line in env_content.splitlines():
    if line.startswith("VITE_SUPABASE_URL="):
        supabase_url = line.split("=", 1)[1].strip()
    elif line.startswith("VITE_SUPABASE_ANON_KEY="):
        supabase_key = line.split("=", 1)[1].strip()

alert = {
    "id": str(uuid.uuid4()),
    "alert_id": f"alert_live_{uuid.uuid4().hex[:8]}",
    "title": "Live AI-Generated Threat Detected",
    "description": "Simulated live threat injected for dashboard testing.",
    "severity": random.choice(["HIGH", "CRITICAL", "MEDIUM"]),
    "attack_type": random.choice(["DDOS_SYN_FLOOD", "C2_BEACONING", "DATA_EXFILTRATION"]),
    "source_ip": f"198.51.100.{random.randint(1,254)}",
    "target_ip": "10.0.10.20",
    "target_port": random.choice([80, 443, 53]),
    "confidence_score": round(random.uniform(0.75, 0.99), 4),
    "contributing_bots": ["ddos_bot", "beaconing_bot"],
    "bot_scores": {"ddos_bot": 0.95},
    "evidence": {"pps": 25000},
    "status": "NEW",
    "blockchain_verified": False,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}

endpoint = f"{supabase_url}/rest/v1/threat_alerts"
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(endpoint, data=json.dumps(alert).encode("utf-8"), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as resp:
        print(f"Successfully triggered live alert! ({resp.status})")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
