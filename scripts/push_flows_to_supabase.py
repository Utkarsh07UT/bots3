#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
import time

SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL", os.environ.get("SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY", os.environ.get("SUPABASE_SERVICE_KEY", ""))

# fallback to checking frontend env if not set in backend
if not SUPABASE_URL:
    try:
        with open(os.path.join(os.path.dirname(__file__), "../frontend/.env"), "r") as f:
            for line in f:
                if line.startswith("VITE_SUPABASE_URL="):
                    SUPABASE_URL = line.strip().split("=")[1].rstrip("/")
                elif line.startswith("VITE_SUPABASE_ANON_KEY="):
                    SUPABASE_KEY = line.strip().split("=")[1]
    except Exception:
        pass

FLOWS_FILE = os.path.join(os.path.dirname(__file__), "../data/flows/sample_mixed_flows.json")

def push_flows():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase URL or Key not found in environment.")
        return

    print(f"Connecting to Supabase REST API: {SUPABASE_URL}")
    print(f"Loading flows from {FLOWS_FILE}...")
    
    with open(FLOWS_FILE, "r") as f:
        flows = json.load(f)
        
    print(f"Loaded {len(flows)} flows. Beginning batch upload...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/network_flows"
    
    # Supabase REST API has a payload limit, so we batch them (e.g., 500 at a time)
    batch_size = 500
    for i in range(0, len(flows), batch_size):
        batch = flows[i:i+batch_size]
        
        # Ensure data types match Supabase schema requirements
        for flow in batch:
            import uuid
            flow["id"] = str(uuid.uuid4())
            flow["flow_id"] = str(uuid.uuid4())[:16]
            if "metadata" in flow:
                flow["extra_metadata"] = flow.pop("metadata")
        
        try:
            import requests
            resp = requests.post(
                endpoint,
                json=batch,
                headers=headers,
                timeout=30
            )
            if not resp.ok:
                print(f"  [!] HTTP Error pushing batch: {resp.status_code} - {resp.text}")
                break
            print(f"  [✓] Batch {i//batch_size + 1} pushed successfully ({len(batch)} flows).")
        except Exception as e:
            print(f"  [!] HTTP Error pushing batch: {e}")
            break
            
        time.sleep(0.5)

    print("\n✅ Supabase ingest complete!")

if __name__ == "__main__":
    push_flows()
