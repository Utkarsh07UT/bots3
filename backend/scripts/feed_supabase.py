import os
import time
import random
import uuid
from datetime import datetime, timezone
import sys
from pathlib import Path

# Add backend dir to path so we can import app modules
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db.session import SessionLocal, Base, engine
from app.db.models import NetworkFlow, ThreatAlert

def generate_mock_data():
    flow_id = str(uuid.uuid4())
    is_malicious = random.random() < 0.35
    
    # 1. Create a Flow
    flow = NetworkFlow(
        flow_id=flow_id,
        src_ip=f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
        dst_ip="10.0.0.5",
        src_port=random.randint(1024, 65535),
        dst_port=random.choice([80, 443, 22, 3389, 53]),
        protocol="TCP",
        pkts_in=random.randint(1, 1000) if not is_malicious else random.randint(5000, 50000),
        bytes_in=random.randint(100, 5000) if not is_malicious else random.randint(1000000, 50000000),
        duration=random.uniform(0.1, 5.0),
        is_attack=is_malicious,
        attack_type="DDoS" if is_malicious else "Normal",
        timestamp=datetime.now(timezone.utc)
    )
    
    # 2. Create an Alert if malicious
    alert = None
    if is_malicious:
        attack_types = ["Ransomware", "Phishing", "Brute Force", "DDoS", "Malware"]
        alert = ThreatAlert(
            flow_id=flow_id,
            threat_type=random.choice(attack_types),
            severity=random.choice(["HIGH", "CRITICAL"]),
            confidence_score=random.uniform(0.85, 0.99),
            mitigation_status="PENDING",
            timestamp=datetime.now(timezone.utc),
            description="Suspicious high-volume traffic detected matching known signature profiles.",
            is_acknowledged=False
        )
        
    return flow, alert

def main():
    db_url = os.getenv("DATABASE_URL", "")
    if "sqlite" in db_url or "[YOUR-DB-PASSWORD]" in db_url:
        print("❌ ERROR: DATABASE_URL in backend/.env is not configured for Supabase.")
        print("Please edit backend/.env and replace [YOUR-DB-PASSWORD] with your actual Supabase password.")
        print(f"Current URL: {db_url}")
        sys.exit(1)
        
    print(f"✅ Connected to: {db_url.split('@')[-1]}")
    print("⏳ Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("🚀 Starting data feed to Supabase! Press Ctrl+C to stop.")
    db = SessionLocal()
    try:
        count = 0
        while True:
            flow, alert = generate_mock_data()
            
            db.add(flow)
            if alert:
                db.add(alert)
                
            db.commit()
            count += 1
            
            if count % 10 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Inserted {count} flows into Supabase...")
                
            time.sleep(1.5)  # Pause between inserts to simulate live traffic
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopped data feed.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
