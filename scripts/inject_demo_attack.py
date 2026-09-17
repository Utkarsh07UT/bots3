#!/usr/bin/env python3
import os
import json
import requests
import uuid
import time
import random
from datetime import datetime, timedelta

# Load Supabase config from frontend/.env
SUPABASE_URL = ""
SUPABASE_KEY = ""

try:
    with open(os.path.join(os.path.dirname(__file__), "../frontend/.env"), "r") as f:
        for line in f:
            if line.startswith("VITE_SUPABASE_URL="):
                SUPABASE_URL = line.strip().split("=")[1].rstrip("/")
            elif line.startswith("VITE_SUPABASE_ANON_KEY="):
                SUPABASE_KEY = line.strip().split("=")[1]
except Exception:
    pass

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase URL or Key not found.")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def inject_alerts():
    print("🚀 Initiating SIH Demo Showcase Attack Injection...")
    
    # We want a massive spike right now. 
    # Let's generate 250 alerts across different vectors
    alerts = []
    
    # 1. 150 DDoS SYN Flood Alerts (High Volume, Low Severity individually, combined Critical)
    for _ in range(150):
        alerts.append({
            "id": str(uuid.uuid4()),
            "alert_id": str(uuid.uuid4()),
            "title": "SYN Flood Detected",
            "description": "Massive volumetric SYN flood detected against border gateway.",
            "severity": "HIGH",
            "attack_type": "SYN Flood",
            "source_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "target_ip": "10.0.0.1",
            "target_port": 443,
            "confidence_score": round(random.uniform(0.85, 0.99), 3),
            "status": "INVESTIGATING",
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(0, 10))).isoformat() + "Z"
        })
        
    # 2. 40 Data Exfiltration Alerts (Sneaky, Critical)
    for _ in range(40):
        alerts.append({
            "id": str(uuid.uuid4()),
            "alert_id": str(uuid.uuid4()),
            "title": "Data Exfiltration Detected",
            "description": "Anomalous outbound data transfer via DNS tunneling.",
            "severity": "CRITICAL",
            "attack_type": "Data Exfiltration",
            "source_ip": "10.0.0.55", # Internal IP being exfiltrated
            "target_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "target_port": 53,
            "confidence_score": round(random.uniform(0.90, 0.99), 3),
            "status": "NEW",
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(0, 15))).isoformat() + "Z"
        })

    # 3. 30 Ransomware / Encrypted Malware (Critical)
    for _ in range(30):
        alerts.append({
            "id": str(uuid.uuid4()),
            "alert_id": str(uuid.uuid4()),
            "title": "Encrypted Malware Detected",
            "description": "Ransomware-like encryption patterns observed over TLS.",
            "severity": "CRITICAL",
            "attack_type": "Encrypted Malware",
            "source_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "target_ip": "10.0.0.100",
            "target_port": 443,
            "confidence_score": round(random.uniform(0.95, 0.99), 3),
            "status": "NEW",
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(0, 20))).isoformat() + "Z"
        })

    # 4. 30 DGA Domains (Medium)
    for _ in range(30):
        alerts.append({
            "id": str(uuid.uuid4()),
            "alert_id": str(uuid.uuid4()),
            "title": "DGA Domain Detected",
            "description": "Domain Generation Algorithm (DGA) activity detected.",
            "severity": "MEDIUM",
            "attack_type": "DGA",
            "source_ip": "10.0.0.22",
            "target_ip": "8.8.8.8",
            "target_port": 53,
            "confidence_score": round(random.uniform(0.70, 0.85), 3),
            "status": "RESOLVED",
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(0, 60))).isoformat() + "Z"
        })

    print(f"Generated {len(alerts)} coordinated attack alerts.")
    
    # Push to Supabase in batches of 50
    batch_size = 50
    for i in range(0, len(alerts), batch_size):
        batch = alerts[i:i+batch_size]
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/threat_alerts",
            headers=HEADERS,
            json=batch
        )
        if resp.status_code not in (200, 201):
            print(f"Failed to push batch: {resp.status_code} - {resp.text}")
        else:
            print(f"Pushed batch {i//batch_size + 1} / {len(alerts)//batch_size + 1}")
        time.sleep(0.2)
        
    print("✅ Demo Showcase Attack injected successfully!")

if __name__ == "__main__":
    inject_alerts()
