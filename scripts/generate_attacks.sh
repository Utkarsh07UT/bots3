#!/usr/bin/env bash
# =============================================================================
# ⚔️ Threat & Attack Traffic Generator (Real Tools & Active Emulators)
# =============================================================================
# Simulates specialized attack vectors using authentic lab traffic engines:
# 1. hping3: High-throughput TCP SYN Flood & UDP Reflection Amplification
# 2. Slowloris: Low-and-slow persistent HTTP resource exhaustion
# 3. dnscat2 / iodine: Covert C2 & data exfiltration over DNS tunnels
# 4. DGArchive DGA algorithms: Real pseudo-random domain generation
# 5. Sandboxed C2 Emulator: Cobalt Strike / Sliver heartbeat beaconing with Gaussian jitter
# =============================================================================

set -e

VECTOR="${1:-all}"  # all | syn_flood | udp_flood | slowloris | dns_tunnel | dga | c2_beacon | nmap_scan
TARGET_IP="${2:-10.0.10.20}"
DURATION="${3:-15}" # seconds
MODE="${4:-simulate}" # simulate | live

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================="
echo "🚨 Launching Lab Attack Traffic Simulation"
echo "Vector: $VECTOR | Target: $TARGET_IP | Duration: ${DURATION}s"
echo "================================================================="

# --- 1. hping3 SYN Flood & UDP Flood ---
run_hping3_syn() {
    echo "[+] [hping3] Simulating TCP SYN Flood on $TARGET_IP:80..."
    if command -v hping3 >/dev/null 2>&1 && [ "$MODE" = "live" ]; then
        sudo hping3 -S --flood -V -p 80 "$TARGET_IP" &
        HPID=$!
        sleep "$DURATION"
        kill -9 "$HPID" 2>/dev/null || true
    else
        python3 -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from scripts.hping3_simulator import Hping3Simulator
flows = Hping3Simulator.generate_syn_flood(count=500, target_ip='$TARGET_IP')
print(f'  [✓] Generated {len(flows)} hping3 TCP SYN flood flows targeting $TARGET_IP:80 (Rate: {flows[0][\"flow_rate_bps\"]} bps)')
"
    fi
}

run_hping3_udp() {
    echo "[+] [hping3] Simulating UDP Flood / Amplification Reflection on $TARGET_IP..."
    if command -v hping3 >/dev/null 2>&1 && [ "$MODE" = "live" ]; then
        sudo hping3 --udp --flood -p 53 "$TARGET_IP" &
        HPID=$!
        sleep "$DURATION"
        kill -9 "$HPID" 2>/dev/null || true
    else
        python3 -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from scripts.hping3_simulator import Hping3Simulator
flows = Hping3Simulator.generate_udp_amp_flood(count=300, victim_ip='$TARGET_IP')
print(f'  [✓] Generated {len(flows)} hping3 UDP reflection amplification flows (DNS/NTP).')
"
    fi
}

# --- 2. Slowloris Slow HTTP Exhaustion ---
run_slowloris() {
    echo "[+] [Slowloris] Simulating low-and-slow HTTP depletion attack..."
    python3 -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from data.generate_datasets import generate_slowloris_flows
flows = generate_slowloris_flows(count=150)
print(f'  [✓] Generated {len(flows)} Slowloris persistent connection exhaustion flows.')
"
}

# --- 3. dnscat2 & iodine DNS Tunneling ---
run_dns_tunnel() {
    echo "[+] [dnscat2 / iodine] Simulating DNS Tunneling & Exfiltration..."
    python3 "$SCRIPT_DIR/dnscat2_tunnel_emulator.py"
}

# --- 4. DGA Domains (DGArchive Algorithms) ---
run_dga() {
    echo "[+] [DGArchive] Simulating Domain Generation Algorithm (DGA) queries..."
    python3 -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from data.threat_intel.dgarchive_dga_generators import generate_all_dga_samples
domains = generate_all_dga_samples(samples_per_family=50)
print(f'  [✓] Generated {len(domains)} DGA domain queries across Cryptolocker, Necurs, Banjori, Suppobox, Mirai, Matsnu, Locky.')
"
}

# --- 5. Sandboxed C2 Emulator (Beaconing Timing) ---
run_c2_beacon() {
    echo "[+] [C2 Emulator] Simulating periodic C2 heartbeat beaconing (Cobalt Strike profile with Gaussian jitter)..."
    python3 "$SCRIPT_DIR/c2_beacon_emulator.py" --count 20 --interval 5.0 --jitter 0.25
}

# --- 6. Nmap Port Scans ---
run_nmap_scan() {
    echo "[+] [Nmap] Simulating vertical and horizontal reconnaissance scans..."
    python3 -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from scripts.hping3_simulator import Hping3Simulator
scans = Hping3Simulator.generate_nmap_scans()
print(f'  [✓] Generated {len(scans)} Nmap vertical port sweeps.')
"
}

# Execute requested vector
case "$VECTOR" in
    syn_flood)
        run_hping3_syn
        ;;
    udp_flood)
        run_hping3_udp
        ;;
    slowloris)
        run_slowloris
        ;;
    dns_tunnel)
        run_dns_tunnel
        ;;
    dga)
        run_dga
        ;;
    c2_beacon)
        run_c2_beacon
        ;;
    nmap_scan)
        run_nmap_scan
        ;;
    all)
        run_hping3_syn
        run_hping3_udp
        run_slowloris
        run_dns_tunnel
        run_dga
        run_c2_beacon
        run_nmap_scan
        ;;
    *)
        echo "Unknown vector: $VECTOR. Options: all | syn_flood | udp_flood | slowloris | dns_tunnel | dga | c2_beacon | nmap_scan"
        exit 1
        ;;
esac

echo "================================================================="
echo "✅ Threat Simulation Completed Successfully!"
echo "================================================================="
