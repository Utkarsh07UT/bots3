"""
tests/test_ai_service.py

Comprehensive test suite verifying the AI Service and all 6 specialist bots:
1. ddos_bot
2. beaconing_bot
3. dga_dns_bot
4. encrypted_malware_bot
5. scanning_bot
6. exfiltration_bot
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_service import app, BOT_NAMES


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["loaded_bots"] == 6
    assert "endpoints" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-threat-detection-bots"
    assert data["bots_loaded"] == 6
    assert set(data["active_bots"]) == set(BOT_NAMES)


def test_list_bots(client):
    response = client.get("/bots")
    assert response.status_code == 200
    bots = response.json()
    assert len(bots) == 6
    bot_names = [b["bot_name"] for b in bots]
    for expected in BOT_NAMES:
        assert expected in bot_names
    for b in bots:
        assert b["status"] == "ONLINE"
        assert b["version"] == "1.0.0"
        assert len(b["features"]) > 0
        assert b["accuracy_score"] > 0.90


def test_get_bot_detail(client):
    for name in BOT_NAMES:
        response = client.get(f"/bots/{name}")
        assert response.status_code == 200
        bot_data = response.json()
        assert bot_data["bot_name"] == name
        assert bot_data["status"] == "ONLINE"


def test_get_invalid_bot(client):
    response = client.get("/bots/non_existent_bot")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Specialist Bot Inference Tests
# ---------------------------------------------------------------------------
def test_ddos_bot_inference(client):
    # Attack payload (SYN flood)
    attack_payload = {
        "duration": 2.5,
        "total_packets": 50000,
        "total_bytes": 50000 * 64,
        "syn_count": 48000,
        "ack_count": 100,
        "fin_count": 0,
        "rst_count": 1000,
        "unique_src_ports": 25000,
    }
    resp = client.post("/predict/ddos_bot", json=attack_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "ddos_bot"
    assert data["malicious"] is True
    assert data["confidence"] >= 0.70

    # Benign payload
    benign_payload = {
        "duration": 15.0,
        "total_packets": 60,
        "total_bytes": 45000,
        "syn_count": 2,
        "ack_count": 2,
        "fin_count": 1,
        "rst_count": 0,
        "unique_src_ports": 1,
    }
    resp = client.post("/predict/ddos_bot", json=benign_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "ddos_bot"
    assert data["malicious"] is False


def test_beaconing_bot_inference(client):
    # Attack payload (Strict periodic C2 heartbeat, low jitter)
    import numpy as np
    intervals = np.random.normal(loc=30.0, scale=0.5, size=30).tolist()
    attack_payload = {"intervals": intervals}

    resp = client.post("/predict/beaconing_bot", json=attack_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "beaconing_bot"
    assert data["malicious"] is True

    # Benign payload (Irregular human browsing intervals)
    benign_payload = {"intervals": [1.2, 45.0, 3.1, 120.5, 0.4, 88.2, 5.0, 210.0]}
    resp = client.post("/predict/beaconing_bot", json=benign_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "beaconing_bot"
    assert data["malicious"] is False


def test_dga_dns_bot_inference(client):
    # Attack payload (Cryptolocker / Kraken style DGA random domain)
    attack_payload = {"domain": "xqz789vnmkp210wqaz.biz"}
    resp = client.post("/predict/dga_dns_bot", json=attack_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "dga_dns_bot"
    assert data["malicious"] is True

    # Benign payload
    benign_payload = {"domain": "github.com"}
    resp = client.post("/predict/dga_dns_bot", json=benign_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "dga_dns_bot"
    assert data["malicious"] is False


def test_encrypted_malware_bot_inference(client):
    # Attack payload (Cobalt Strike JA3 hash / minimal cipher suites)
    attack_payload = {
        "ja3_hash": "a0e9f5d64349fb13191bc781f81f42e1",
        "cipher_suite_count": 2,
        "extension_count": 1,
        "handshake_duration_ms": 10.0,
        "session_duration": 120.0,
        "sni_length": 5,
        "packet_sizes": [256, 256, 256, 256, 256],
    }
    resp = client.post("/predict/encrypted_malware_bot", json=attack_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "encrypted_malware_bot"
    assert data["malicious"] is True

    # Benign payload (Standard browser rich TLS profile)
    benign_payload = {
        "cipher_suite_count": 18,
        "extension_count": 14,
        "handshake_duration_ms": 75.0,
        "session_duration": 45.0,
        "sni_length": 16,
        "packet_sizes": [120, 850, 1420, 64, 1100, 300, 1500],
    }
    resp = client.post("/predict/encrypted_malware_bot", json=benign_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "encrypted_malware_bot"
    assert data["malicious"] is False


def test_scanning_bot_inference(client):
    # Attack payload (Port sweep touching thousands of destination ports)
    attack_payload = {
        "unique_dst_ips": 1,
        "unique_dst_ports": 20000,
        "syn_count": 20000,
        "synack_count": 10,
        "total_packets": 20010,
        "duration": 5.0,
    }
    resp = client.post("/predict/scanning_bot", json=attack_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "scanning_bot"
    assert data["malicious"] is True

    # Benign payload
    benign_payload = {
        "unique_dst_ips": 2,
        "unique_dst_ports": 2,
        "syn_count": 2,
        "synack_count": 2,
        "total_packets": 50,
        "duration": 20.0,
    }
    resp = client.post("/predict/scanning_bot", json=benign_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "scanning_bot"
    assert data["malicious"] is False


def test_exfiltration_bot_inference(client):
    # Attack payload (Huge outbound volume, anomalous out/in ratio, high entropy DNS TXT)
    attack_payload = {
        "outbound_bytes": 15000000,
        "inbound_bytes": 2000,
        "out_in_ratio": 7500.0,
        "duration": 120.0,
        "request_count": 500,
        "dns_txt_avg_size": 220.0,
        "payload_entropy": 7.8,
    }
    resp = client.post("/predict/exfiltration_bot", json=attack_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "exfiltration_bot"
    assert data["malicious"] is True

    # Benign payload (Normal browsing: high inbound download, low outbound)
    benign_payload = {
        "outbound_bytes": 5000,
        "inbound_bytes": 500000,
        "out_in_ratio": 0.01,
        "duration": 30.0,
        "request_count": 25,
        "dns_txt_avg_size": 20.0,
        "payload_entropy": 3.2,
    }
    resp = client.post("/predict/exfiltration_bot", json=benign_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_name"] == "exfiltration_bot"
    assert data["malicious"] is False


def test_batch_prediction(client):
    items = [
        {"duration": 1.0, "total_packets": 80000, "total_bytes": 5000000, "syn_count": 78000, "ack_count": 100, "unique_src_ports": 30000},
        {"duration": 20.0, "total_packets": 40, "total_bytes": 30000, "syn_count": 2, "ack_count": 2, "unique_src_ports": 1},
    ]
    resp = client.post("/predict/batch/ddos_bot", json=items)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 2
    assert results[0]["malicious"] is True
    assert results[1]["malicious"] is False


def test_predict_all_fusion(client):
    flow_telemetry = {
        "flow_id": "test-flow-uuid-1234",
        "duration": 2.0,
        "total_packets": 60000,
        "syn_count": 58000,
        "unique_src_ports": 20000,
        "domain": "google.com",
    }
    resp = client.post("/predict/all", json=flow_telemetry)
    assert resp.status_code == 200
    data = resp.json()
    assert data["flow_id"] == "test-flow-uuid-1234"
    assert data["evaluated_bots_count"] == 6
    assert data["threat_detected"] is True
    assert "ddos_bot" in data["contributing_bots"]
    assert "ddos_bot" in data["predictions"]
