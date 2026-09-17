import random
import uuid

attacks = [
    ("DDoS", 443, "CRITICAL", 0.99, ARRAY_BOTS:="['ddos_bot']", "High volume SYN flood."),
    ("Brute Force", 22, "HIGH", 0.92, ARRAY_BOTS:="['scanning_bot']", "Repeated SSH login failures."),
    ("Malware", 443, "HIGH", 0.95, ARRAY_BOTS:="['encrypted_malware_bot']", "Suspicious JA3 TLS signature."),
    ("Phishing", 80, "MEDIUM", 0.88, ARRAY_BOTS:="['dga_dns_bot']", "Connecting to suspected typo-squatted domain."),
    ("Exfiltration", 53, "CRITICAL", 0.97, ARRAY_BOTS:="['exfiltration_bot']", "Massive outbound DNS TXT records.")
]

countries = ["US", "CN", "RU", "IR", "KP", "BR", "IN", "DE", "FR", "NL"]

sql = "INSERT INTO network_flows (id, flow_id, src_ip, dst_ip, src_port, dst_port, protocol, duration, bytes_in, bytes_out, pkts_in, pkts_out, tcp_flags, is_attack, attack_type, timestamp, extra_metadata) VALUES\n"

alerts_sql = "INSERT INTO threat_alerts (id, alert_id, title, description, severity, attack_type, source_ip, target_ip, target_port, confidence_score, contributing_bots, bot_scores, evidence, status, blockchain_verified, created_at, updated_at) VALUES\n"

flow_values = []
alert_values = []

for i in range(30):
    is_attack = random.random() < 0.4
    src_ip = f"{random.randint(1,220)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    flow_id = str(uuid.uuid4())
    country = random.choice(countries)
    
    if is_attack:
        attack = random.choice(attacks)
        flow_values.append(f"(gen_random_uuid()::text, '{flow_id}', '{src_ip}', '10.0.0.5', {random.randint(1024, 65000)}, {attack[1]}, 'TCP', {random.uniform(0.1, 60.0):.2f}, {random.randint(1000, 100000)}, {random.randint(100, 50000)}, {random.randint(10, 5000)}, {random.randint(10, 500)}, 'SYN', true, '{attack[0]}', now() - interval '{random.randint(1, 120)} seconds', '{{\"country\": \"{country}\"}}'::json)")
        
        alert_values.append(f"(gen_random_uuid()::text, 'ALT-{attack[0][:3].upper()}-{random.randint(1000,9999)}', '{attack[0]} Detected', '{attack[5]}', '{attack[2]}', '{attack[0]}', '{src_ip}', '10.0.0.5', {attack[1]}, {attack[3]}, ARRAY{attack[4]}, '{{\"score\": {attack[3]}}}'::json, '{{\"matched_rules\": 1}}'::json, 'NEW', false, now() - interval '{random.randint(1, 120)} seconds', now())")
    else:
        flow_values.append(f"(gen_random_uuid()::text, '{flow_id}', '{src_ip}', '10.0.0.5', {random.randint(1024, 65000)}, 443, 'TCP', {random.uniform(0.1, 5.0):.2f}, {random.randint(100, 5000)}, {random.randint(1000, 20000)}, {random.randint(5, 50)}, {random.randint(10, 100)}, 'ACK', false, 'BENIGN', now() - interval '{random.randint(1, 120)} seconds', '{{\"country\": \"{country}\"}}'::json)")

with open("backend/scripts/massive_seed.sql", "w") as f:
    f.write("-- BULK NETWORK FLOWS\n")
    f.write(sql + ",\n".join(flow_values) + ";\n\n")
    f.write("-- BULK THREAT ALERTS\n")
    f.write(alerts_sql + ",\n".join(alert_values) + ";\n")

