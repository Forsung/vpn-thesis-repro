#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./baseline_test.sh <vpn_name> <server_vpn_ip> <duration_sec> [output_base_dir]
#
# Example:
#   ./baseline_test.sh wireguard 10.10.0.1 60 ~/vpn-thesis/results
#
# Assumptions:
# - VPN tunnel is already up
# - iperf3 server is running on the server side
# - You want a clean baseline with no tc/netem impairment

VPN_NAME="${1:-}"
SERVER_IP="${2:-}"
DURATION="${3:-60}"
BASE_DIR="${4:-$HOME/vpn-thesis/results}"

if [[ -z "$VPN_NAME" || -z "$SERVER_IP" ]]; then
  echo "Usage: $0 <vpn_name> <server_vpn_ip> <duration_sec> [output_base_dir]"
  exit 1
fi

TS="$(date -u +%Y%m%dT%H%M%SZ)"
HOST="$(hostname)"
RUN_ID="${VPN_NAME}_${HOST}_${TS}"
OUTDIR="${BASE_DIR}/${RUN_ID}"
mkdir -p "$OUTDIR"

echo "[*] Saving environment and runtime info..."
{
  echo "run_id=$RUN_ID"
  echo "vpn=$VPN_NAME"
  echo "host=$HOST"
  echo "server_ip=$SERVER_IP"
  echo "timestamp_utc=$TS"
  echo "duration_sec=$DURATION"
  echo
  uname -a
  echo
  lsb_release -a 2>/dev/null || true
  echo
  ip route show
  echo
  ip addr show
} > "$OUTDIR/environment.txt"

if command -v wg >/dev/null 2>&1; then
  wg show > "$OUTDIR/wg_show.txt" 2>/dev/null || true
fi

if command -v ipsec >/dev/null 2>&1; then
  ipsec statusall > "$OUTDIR/ipsec_status.txt" 2>/dev/null || true
fi

if command -v openvpn >/dev/null 2>&1; then
  openvpn --version > "$OUTDIR/openvpn_version.txt" 2>/dev/null || true
fi

echo "[*] Measuring ping..."
ping -i 0.2 -c 50 "$SERVER_IP" | tee "$OUTDIR/ping.log"

echo "[*] Measuring TCP throughput..."
iperf3 -c "$SERVER_IP" -t "$DURATION" -J > "$OUTDIR/iperf_tcp.json"

echo "[*] Measuring UDP throughput/loss/jitter..."
iperf3 -c "$SERVER_IP" -u -b 50M -t "$DURATION" -J > "$OUTDIR/iperf_udp.json"

echo "[*] Capturing CPU and memory usage..."
python3 - <<'EOF' > "$OUTDIR/cpu_mem.json"
import json, time
try:
    import psutil
except ImportError:
    raise SystemExit("psutil is missing. Install with: pip3 install psutil")

samples = []
for _ in range(60):
    samples.append({
        "ts": time.time(),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "mem_percent": psutil.virtual_memory().percent,
    })
    time.sleep(1)

print(json.dumps(samples, indent=2))
EOF

echo "[*] Measuring handshake/reconnect timing (quick restart of the tunnel is NOT done here)."
echo "If you want handshake timing, measure it separately when restarting the VPN tunnel." \
  > "$OUTDIR/notes.txt"

echo "[*] Saving metadata..."
cat > "$OUTDIR/metadata.json" <<EOF
{
  "run_id": "$RUN_ID",
  "vpn": "$VPN_NAME",
  "host": "$HOST",
  "server_ip": "$SERVER_IP",
  "timestamp_utc": "$TS",
  "duration_sec": $DURATION,
  "mode": "baseline"
}
EOF

echo "[*] Done. Results saved in: $OUTDIR"
