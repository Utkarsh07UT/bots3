import json
import uuid
from inject_demo_attack import inject_alerts
import inject_demo_attack

def patched_inject():
    import random
    from datetime import datetime, timedelta
    alerts = []
    
    def base_alert(type_, severity_, title, desc):
        return {
            "id": str(uuid.uuid4()),
            "alert_id": str(uuid.uuid4()),
            "title": title,
            "description": desc,
            "severity": severity_,
            "attack_type": type_,
            "source_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "target_ip": "10.0.0.1",
            "target_port": 443,
            "confidence_score": round(random.uniform(0.85, 0.99), 3),
            "status": "INVESTIGATING",
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(0, 10))).isoformat() + "Z",
            "contributing_bots": ["ddos_bot", "exfiltration_bot"],
            "bot_scores": {"ddos_bot": 0.99},
            "evidence": {},
            "blockchain_verified": False
        }

    for _ in range(150):
        alerts.append(base_alert("SYN Flood", "HIGH", "SYN Flood Detected", "Massive volumetric SYN flood detected against border gateway."))
        
    for _ in range(40):
        a = base_alert("Data Exfiltration", "CRITICAL", "Data Exfiltration Detected", "Anomalous outbound data transfer via DNS tunneling.")
        a["source_ip"] = "10.0.0.55"
        a["target_port"] = 53
        a["status"] = "NEW"
        alerts.append(a)

    for _ in range(30):
        a = base_alert("Encrypted Malware", "CRITICAL", "Encrypted Malware Detected", "Ransomware-like encryption patterns observed over TLS.")
        a["status"] = "NEW"
        alerts.append(a)

    for _ in range(30):
        a = base_alert("DGA", "MEDIUM", "DGA Domain Detected", "Domain Generation Algorithm (DGA) activity detected.")
        a["target_ip"] = "8.8.8.8"
        a["target_port"] = 53
        a["status"] = "RESOLVED"
        alerts.append(a)

    import requests, time
    batch_size = 50
    for i in range(0, len(alerts), batch_size):
        batch = alerts[i:i+batch_size]
        resp = requests.post(
            f"{inject_demo_attack.SUPABASE_URL}/rest/v1/threat_alerts",
            headers=inject_demo_attack.HEADERS,
            json=batch
        )
        if resp.status_code not in (200, 201):
            print(f"Failed to push batch: {resp.status_code} - {resp.text}")
        else:
            print(f"Pushed batch {i//batch_size + 1} / {len(alerts)//batch_size + 1}")
        time.sleep(0.2)
        
patched_inject()
