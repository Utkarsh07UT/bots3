-- ============================================================================
-- 🛡️ Supabase Data Seeding Script for Cyber Threat Detection
-- Run this directly in your Supabase SQL Editor to populate the dashboard!
-- ============================================================================

-- 1. Insert Mock Network Flows
INSERT INTO network_flows (
    id, flow_id, src_ip, dst_ip, src_port, dst_port, protocol, 
    duration, bytes_in, bytes_out, pkts_in, pkts_out, tcp_flags, 
    flow_rate_bps, packet_rate_pps, entropy, is_attack, attack_type, 
    timestamp, extra_metadata
)
VALUES
-- Benign Flow 1
(gen_random_uuid()::text, gen_random_uuid()::text, '192.168.1.45', '10.0.0.5', 54321, 443, 'TCP', 
 1.25, 3450, 8900, 15, 20, 'SYN-ACK', 2760.00, 12.00, 0.45, false, 'BENIGN', 
 now() - interval '5 seconds', '{}'::json),

-- Benign Flow 2
(gen_random_uuid()::text, gen_random_uuid()::text, '192.168.1.102', '10.0.0.5', 61234, 80, 'TCP', 
 0.45, 1200, 4500, 8, 12, 'SYN-ACK', 2666.67, 17.78, 0.32, false, 'BENIGN', 
 now() - interval '4 seconds', '{}'::json),

-- Malicious DDoS Flow
(gen_random_uuid()::text, 'ddos-flow-999', '114.12.34.19', '10.0.0.5', 33452, 443, 'TCP', 
 12.50, 4500000, 0, 15000, 0, 'SYN', 360000.00, 1200.00, 0.15, true, 'DDoS', 
 now() - interval '2 seconds', '{"country": "CN", "asn": "AS4134"}'::json),

-- Malicious Beaconing Flow
(gen_random_uuid()::text, 'beacon-flow-888', '45.33.22.11', '10.0.0.5', 44321, 443, 'TCP', 
 3600.00, 520, 480, 10, 10, 'PSH-ACK', 1.44, 0.00, 7.85, true, 'Malware', 
 now() - interval '1 second', '{"country": "RU", "asn": "AS20473"}'::json);


-- 2. Insert Corresponding Threat Alerts
INSERT INTO threat_alerts (
    id, alert_id, title, description, severity, attack_type, 
    source_ip, target_ip, target_port, confidence_score, 
    contributing_bots, bot_scores, evidence, status, 
    blockchain_verified, created_at, updated_at
)
VALUES
-- DDoS Alert
(gen_random_uuid()::text, 'ALT-DDOS-' || floor(random() * 10000)::text, 'Massive TCP SYN Flood Detected', 
 'High-volume asymmetric traffic spike detected targeting the primary web gateway. Anomaly threshold exceeded by 400%.', 
 'CRITICAL', 'DDoS', '114.12.34.19', '10.0.0.5', 443, 0.9950, 
 ARRAY['ddos_bot', 'scanning_bot'], 
 '{"ddos_bot": 0.998, "scanning_bot": 0.850}'::json, 
 '{"packets_per_second": 1200, "syn_ratio": 0.98, "flow_duration_sec": 12.5}'::json, 
 'NEW', false, now() - interval '2 seconds', now() - interval '2 seconds'),

-- Beaconing / Malware Alert
(gen_random_uuid()::text, 'ALT-C2-' || floor(random() * 10000)::text, 'Advanced Persistent Threat: C2 Beaconing', 
 'Highly regular, low-volume encrypted callbacks to a known suspicious ASN. High payload entropy suggests encrypted malware command channel.', 
 'HIGH', 'Malware', '45.33.22.11', '10.0.0.5', 443, 0.9420, 
 ARRAY['beaconing_bot', 'encrypted_malware_bot'], 
 '{"beaconing_bot": 0.955, "encrypted_malware_bot": 0.920}'::json, 
 '{"jitter_ms": 15, "payload_entropy": 7.85, "interval_sec": 300}'::json, 
 'INVESTIGATING', false, now() - interval '1 second', now() - interval '1 second');

-- 3. (Optional) Initialize Bot Metrics to show them as ONLINE
INSERT INTO bot_metrics (
    id, bot_name, display_name, status, version, 
    latency_ms, cpu_percent, memory_mb, predictions_count, threats_detected,
    accuracy_score, f1_score, last_heartbeat
)
VALUES 
(gen_random_uuid()::text, 'ddos_bot', 'DDoS Detection', 'ONLINE', '1.0.0', 12.5, 4.2, 128.5, 15420, 85, 0.995, 0.991, now()),
(gen_random_uuid()::text, 'beaconing_bot', 'Beaconing Detection', 'ONLINE', '1.0.0', 45.2, 2.1, 256.0, 8400, 12, 0.982, 0.975, now()),
(gen_random_uuid()::text, 'dga_dns_bot', 'DGA / DNS Detection', 'ONLINE', '1.0.0', 8.4, 1.5, 95.0, 42000, 310, 0.965, 0.950, now()),
(gen_random_uuid()::text, 'encrypted_malware_bot', 'Encrypted Malware', 'ONLINE', '1.0.0', 115.0, 18.4, 512.0, 3200, 5, 0.920, 0.890, now()),
(gen_random_uuid()::text, 'scanning_bot', 'Scanning Detection', 'ONLINE', '1.0.0', 5.2, 8.5, 150.0, 85000, 1200, 0.999, 0.998, now()),
(gen_random_uuid()::text, 'exfiltration_bot', 'Data Exfiltration', 'ONLINE', '1.0.0', 85.0, 12.0, 420.0, 1200, 2, 0.940, 0.930, now())
ON CONFLICT (bot_name) DO UPDATE 
SET status = 'ONLINE', last_heartbeat = now();
