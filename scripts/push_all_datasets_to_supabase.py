#!/usr/bin/env python3
import os
import json
import glob
import requests
import uuid
import time

# Resolve Supabase config
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL", os.environ.get("SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY", os.environ.get("SUPABASE_SERVICE_KEY", ""))

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

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase URL or Key not found in environment.")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def pad_keys(batch):
    # PostgREST requires all objects in an array payload to have exactly the same keys.
    all_keys = set()
    for row in batch:
        all_keys.update(row.keys())
    for row in batch:
        for key in all_keys:
            if key not in row or row[key] is None:
                row[key] = None

def transform_flow(row):
    row["id"] = str(uuid.uuid4())
    if "flow_id" not in row:
        row["flow_id"] = str(uuid.uuid4())[:16]
    else:
        row["flow_id"] = row["flow_id"] + "_" + str(uuid.uuid4())[:6]
    
    if "metadata" in row:
        row["extra_metadata"] = row.pop("metadata")
    if "extra_metadata" not in row:
        row["extra_metadata"] = None
        
    for k in ["bytes_in", "bytes_out", "pkts_in", "pkts_out"]:
        if k not in row or row[k] is None: row[k] = 0
    for k in ["duration", "flow_rate_bps", "packet_rate_pps", "entropy"]:
        if k not in row or row[k] is None: row[k] = 0.0
    if "tcp_flags" not in row or row["tcp_flags"] is None: row["tcp_flags"] = "SYN-ACK"
    if "is_attack" not in row or row["is_attack"] is None: row["is_attack"] = False
    if "attack_type" not in row or row["attack_type"] is None: row["attack_type"] = "BENIGN"

def transform_dns(row):
    row["id"] = str(uuid.uuid4())
    if "query_id" not in row:
        row["query_id"] = str(uuid.uuid4())[:16]
    else:
        row["query_id"] = row["query_id"] + "_" + str(uuid.uuid4())[:6]
    if "metadata" in row:
        row.pop("metadata")
        
    if "payload_size_bytes" not in row or row["payload_size_bytes"] is None: row["payload_size_bytes"] = 0
    if "entropy" not in row or row["entropy"] is None: row["entropy"] = 0.0
    if "is_tunneling" not in row or row["is_tunneling"] is None: row["is_tunneling"] = False
    if "tunneling_score" not in row or row["tunneling_score"] is None: row["tunneling_score"] = 0.0

def transform_dga(row):
    row["id"] = str(uuid.uuid4())
    if "confidence" not in row or row["confidence"] is None:
        row["confidence"] = 0.0
    if "entropy" not in row or row["entropy"] is None: row["entropy"] = 0.0
    if "vowel_ratio" not in row or row["vowel_ratio"] is None: row["vowel_ratio"] = 0.0
    if "length" not in row or row["length"] is None: row["length"] = 0
    if "is_dga" not in row or row["is_dga"] is None: row["is_dga"] = False
    row.pop("domain_id", None)
    row.pop("dga_source", None)

def push_data(endpoint, data, table_name, transform_func=None):
    if not data:
        return
    print(f"Uploading {len(data)} records to {table_name}...")
    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        for row in batch:
            if transform_func:
                transform_func(row)
        pad_keys(batch)
        try:
            resp = requests.post(endpoint, json=batch, headers=HEADERS, timeout=30)
            if not resp.ok:
                print(f"  [!] HTTP Error on batch: {resp.status_code} - {resp.text}")
                break
            print(f"  [✓] Batch {i//batch_size + 1} pushed successfully ({len(batch)} records).")
        except Exception as e:
            print(f"  [!] HTTP Error pushing batch: {e}")
            break
        time.sleep(0.5)

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "../data")
    
    # 1. Gather all flow JSONs
    flow_files = glob.glob(f"{base_dir}/**/*flows.json", recursive=True)
    flow_files.append(os.path.join(base_dir, "flows/multi_stage_scenario.json"))
    
    all_flows = []
    for f in flow_files:
        if os.path.exists(f):
            with open(f, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    all_flows.extend(data)
                    
    print(f"Found {len(all_flows)} network flows across {len(flow_files)} files.")
    push_data(f"{SUPABASE_URL}/rest/v1/network_flows?on_conflict=flow_id", all_flows, "network_flows", transform_flow)

    # 2. Gather DNS queries (Only DNS tunneling queries)
    dns_files = [os.path.join(base_dir, "synthetic/attacks/dns_tunneling/dns_tunneling_queries.json")]
    all_dns = []
    for f in dns_files:
        if os.path.exists(f):
            with open(f, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    all_dns.extend(data)
                    
    print(f"\nFound {len(all_dns)} DNS queries across {len(dns_files)} files.")
    push_data(f"{SUPABASE_URL}/rest/v1/dns_queries?on_conflict=query_id", all_dns, "dns_queries", transform_dns)

    # 3. Gather DGA domains (Both dga_domains and dga_queries)
    dga_files = [
        os.path.join(base_dir, "synthetic/attacks/dga_samples/dga_domains.json"),
        os.path.join(base_dir, "synthetic/attacks/dga_samples/dga_queries.json")
    ]
    all_dga = []
    for f in dga_files:
        if os.path.exists(f):
            with open(f, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    all_dga.extend(data)
                    
    print(f"\nFound {len(all_dga)} DGA domains across {len(dga_files)} files.")
    # Deduplicate by domain
    unique_dga = {}
    for d in all_dga:
        domain = d.get("domain")
        if domain:
            unique_dga[domain] = d
    all_dga = list(unique_dga.values())
    
    push_data(f"{SUPABASE_URL}/rest/v1/dga_domains?on_conflict=domain", all_dga, "dga_domains", transform_dga)
    
    print("\n✅ All datasets have been pushed to Supabase!")

if __name__ == "__main__":
    main()
