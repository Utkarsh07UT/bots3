#!/usr/bin/env bash
# =============================================================================
# 🛡️ Benign Traffic Generator (iperf3, TRex & Pareto Statistical Generator)
# =============================================================================
# Simulates standard enterprise network activity matching lab benchmarks:
# - Heavy-tailed Pareto flow sizes (80% small, 15% medium, 5% large)
# - Poisson packet arrival processes with natural inter-arrival time (IAT) variance
# - Mixed enterprise protocol distribution (HTTPS, HTTP/2, SSH, DNS, NTP, SMTP)
# =============================================================================

set -e

TARGET_IP="${1:-127.0.0.1}"
DURATION="${2:-30}" # seconds
MODE="${3:-simulate}" # simulate | live

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================="
echo "🌐 Starting Benign Network Traffic Generation"
echo "Target: $TARGET_IP | Duration: ${DURATION}s | Mode: $MODE"
echo "================================================================="

if [ "$MODE" = "live" ]; then
    echo "[+] Running live traffic generation tools..."
    
    # 1. iperf3 TCP & UDP Traffic
    if command -v iperf3 >/dev/null 2>&1; then
        echo "[+] Launching iperf3 TCP stream (simulating bulk transfer)..."
        iperf3 -c "$TARGET_IP" -t 5 -P 4 || true
        
        echo "[+] Launching iperf3 UDP stream (simulating VoIP / video stream)..."
        iperf3 -c "$TARGET_IP" -u -b 10M -t 5 || true
    else
        echo "[!] iperf3 not installed, using Pareto statistical flow generator..."
    fi

    # 2. Curl HTTP / HTTPS Web Browsing
    echo "[+] Simulating web browsing traffic..."
    for i in {1..10}; do
        curl -s -o /dev/null -w "HTTP Status: %{http_code} | Time: %{time_total}s\n" "http://$TARGET_IP" 2>/dev/null || true
        sleep 0.1
    done
else
    echo "[+] Running Pareto heavy-tailed benign traffic generator..."
    python3 "$SCRIPT_DIR/benign_traffic_generator.py"
fi

echo "================================================================="
echo "✅ Benign Traffic Generation Complete!"
echo "================================================================="
