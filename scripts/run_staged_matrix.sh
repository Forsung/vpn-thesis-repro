#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run_staged_matrix.sh vm
#   ./run_staged_matrix.sh pi
#
# Runs the staged matrix in this order:
#   baseline -> latency -> loss -> mtu -> cpu_stress -> mobility
#
# Notes:
# - Run this on the client machine.
# - Start iperf3 server on the VPS before running.
# - IPsec is run only for vm, not for pi.

ROLE="${1:-}"
if [[ -z "$ROLE" ]]; then
  echo "Usage: $0 <vm|pi>"
  exit 1
fi

BASE_DIR="$HOME/vpn-thesis/results"
SCRIPT_DIR="$HOME/vpn-thesis/scripts"
TEST_SYSTEM="$SCRIPT_DIR/test_system.py"

REPEATS=3
DURATION=60
PING_COUNT=50
UDP_BW="50M"

if [[ "$ROLE" == "vm" ]]; then
  IFACE="enp0s3"
  WG_SERVER_IP="10.10.0.1"
  OVPN_SERVER_IP="10.20.0.1"
  IPSEC_SERVER_IP="192.168.1.175"
  OVPN_CLIENT_CONF="$HOME/vm-client.ovpn"
elif [[ "$ROLE" == "pi" ]]; then
  IFACE="eth0"
  WG_SERVER_IP="10.10.0.1"
  OVPN_SERVER_IP="10.20.0.1"
  OVPN_CLIENT_CONF="$HOME/pi-client.ovpn"
else
  echo "Invalid role: $ROLE"
  exit 1
fi

cleanup_vpn() {
  sudo wg-quick down wg0 2>/dev/null || true
  sudo pkill openvpn 2>/dev/null || true
  sudo ipsec down ikev2-client 2>/dev/null || true
}

run_case() {
  local stage="$1"
  local vpn="$2"
  local server_ip="$3"
  local repeat_id="$4"
  shift 4

  cleanup_vpn

  python3 "$TEST_SYSTEM" \
    --stage "$stage" \
    --vpn "$vpn" \
    --server-ip "$server_ip" \
    --iface "$IFACE" \
    --duration "$DURATION" \
    --ping-count "$PING_COUNT" \
    --udp-bandwidth "$UDP_BW" \
    --start-vpn \
    --stop-vpn \
    --clear-netem \
    --measure-handshake \
    "$@" \
    --repeat-id "$repeat_id"
}

run_stage() {
  local stage="$1"
  echo "=================================================="
  echo "STAGE: $stage"
  echo "ROLE : $ROLE"
  echo "=================================================="

  case "$stage" in
    baseline)
      for r in $(seq 1 "$REPEATS"); do
        echo "[baseline] WireGuard run $r"
        run_case baseline wireguard "$WG_SERVER_IP" "$r" --mtu 1500 --capture

        echo "[baseline] OpenVPN run $r"
        run_case baseline openvpn "$OVPN_SERVER_IP" "$r" --client-conf "$OVPN_CLIENT_CONF" --mtu 1500 --capture

        if [[ "$ROLE" == "vm" ]]; then
          echo "[baseline] IPsec run $r"
          run_case baseline ipsec "$IPSEC_SERVER_IP" "$r" --mtu 1500 --capture
        fi
      done
      ;;

    latency)
      for r in $(seq 1 "$REPEATS"); do
        echo "[latency] WireGuard run $r"
        run_case latency wireguard "$WG_SERVER_IP" "$r" --delay 50 --mtu 1500 --capture

        echo "[latency] OpenVPN run $r"
        run_case latency openvpn "$OVPN_SERVER_IP" "$r" --client-conf "$OVPN_CLIENT_CONF" --delay 50 --mtu 1500 --capture

        if [[ "$ROLE" == "vm" ]]; then
          echo "[latency] IPsec run $r"
          run_case latency ipsec "$IPSEC_SERVER_IP" "$r" --delay 50 --mtu 1500 --capture
        fi
      done
      ;;

    loss)
      for r in $(seq 1 "$REPEATS"); do
        echo "[loss] WireGuard run $r"
        run_case loss wireguard "$WG_SERVER_IP" "$r" --loss 1 --mtu 1500 --capture

        echo "[loss] OpenVPN run $r"
        run_case loss openvpn "$OVPN_SERVER_IP" "$r" --client-conf "$OVPN_CLIENT_CONF" --loss 1 --mtu 1500 --capture

        if [[ "$ROLE" == "vm" ]]; then
          echo "[loss] IPsec run $r"
          run_case loss ipsec "$IPSEC_SERVER_IP" "$r" --loss 1 --mtu 1500 --capture
        fi
      done
      ;;

    mtu)
      for r in $(seq 1 "$REPEATS"); do
        echo "[mtu1400] WireGuard run $r"
        run_case mtu wireguard "$WG_SERVER_IP" "$r" --mtu 1400 --capture

        echo "[mtu1400] OpenVPN run $r"
        run_case mtu openvpn "$OVPN_SERVER_IP" "$r" --client-conf "$OVPN_CLIENT_CONF" --mtu 1400 --capture

        if [[ "$ROLE" == "vm" ]]; then
          echo "[mtu1400] IPsec run $r"
          run_case mtu ipsec "$IPSEC_SERVER_IP" "$r" --mtu 1400 --capture
        fi
      done
      ;;

    cpu_stress)
      for r in $(seq 1 "$REPEATS"); do
        echo "[cpu_stress] WireGuard run $r"
        run_case cpu_stress wireguard "$WG_SERVER_IP" "$r" --mtu 1500 --capture --cpu-stress

        echo "[cpu_stress] OpenVPN run $r"
        run_case cpu_stress openvpn "$OVPN_SERVER_IP" "$r" --client-conf "$OVPN_CLIENT_CONF" --mtu 1500 --capture --cpu-stress

        if [[ "$ROLE" == "vm" ]]; then
          echo "[cpu_stress] IPsec run $r"
          run_case cpu_stress ipsec "$IPSEC_SERVER_IP" "$r" --mtu 1500 --capture --cpu-stress
        fi
      done
      ;;

    mobility)
      for r in $(seq 1 "$REPEATS"); do
        echo "[mobility] WireGuard run $r"
        run_case mobility wireguard "$WG_SERVER_IP" "$r" --mtu 1500 --capture --measure-reconnect

        echo "[mobility] OpenVPN run $r"
        run_case mobility openvpn "$OVPN_SERVER_IP" "$r" --client-conf "$OVPN_CLIENT_CONF" --mtu 1500 --capture --measure-reconnect

        if [[ "$ROLE" == "vm" ]]; then
          echo "[mobility] IPsec run $r"
          run_case mobility ipsec "$IPSEC_SERVER_IP" "$r" --mtu 1500 --capture --measure-reconnect
        fi
      done
      ;;

    all)
      run_stage baseline
      run_stage latency
      run_stage loss
      run_stage mtu
      run_stage cpu_stress
      run_stage mobility
      ;;

    *)
      echo "Unknown stage: $stage"
      echo "Use: baseline | latency | loss | mtu | cpu_stress | mobility | all"
      exit 1
      ;;
  esac
}

mkdir -p "$BASE_DIR"
echo "[*] Starting staged matrix for role: $ROLE"
echo "[*] Results will be stored under: $BASE_DIR"

run_stage baseline

echo "[*] Done."
