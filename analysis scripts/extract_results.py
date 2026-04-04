from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(r"C:\vpn-thesis\results")
OUT_DIR = Path(r"C:\vpn-thesis\analysis\outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def parse_ping_avg(ping_text: str):
    m = re.search(r"= ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms", ping_text)
    if m:
        return {
            "rtt_min_ms": float(m.group(1)),
            "rtt_avg_ms": float(m.group(2)),
            "rtt_max_ms": float(m.group(3)),
            "rtt_mdev_ms": float(m.group(4)),
        }

    m = re.search(r"round-trip.*= ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms", ping_text)
    if m:
        return {
            "rtt_min_ms": float(m.group(1)),
            "rtt_avg_ms": float(m.group(2)),
            "rtt_max_ms": float(m.group(3)),
            "rtt_mdev_ms": float(m.group(4)),
        }

    return {
        "rtt_min_ms": None,
        "rtt_avg_ms": None,
        "rtt_max_ms": None,
        "rtt_mdev_ms": None,
    }


def extract_iperf_tcp_bits_per_sec(obj):
    if not obj or "end" not in obj:
        return None

    end = obj["end"]

    if "sum_received" in end and "bits_per_second" in end["sum_received"]:
        return end["sum_received"]["bits_per_second"]

    if "sum" in end and "bits_per_second" in end["sum"]:
        return end["sum"]["bits_per_second"]

    for key in ["streams", "sum_sent", "sum_received"]:
        if key in end:
            val = end[key]
            if isinstance(val, dict) and "bits_per_second" in val:
                return val["bits_per_second"]

    return None


def extract_udp_fields(obj):
    if not obj or "end" not in obj:
        return {
            "udp_bits_per_sec": None,
            "udp_loss_pct": None,
            "udp_jitter_ms": None,
        }

    end = obj["end"]
    s = end.get("sum", {})

    return {
        "udp_bits_per_sec": s.get("bits_per_second"),
        "udp_loss_pct": s.get("lost_percent"),
        "udp_jitter_ms": s.get("jitter_ms"),
    }


def detect_client_type(meta):
    iface = meta.get("iface")

    if iface == "enp0s3":
        return "VM"
    elif iface == "eth0":
        return "RaspberryPi"
    else:
        return "Unknown"


rows = []

for run_dir in sorted(BASE_DIR.iterdir()):
    if not run_dir.is_dir():
        continue

    meta_path = run_dir / "metadata.json"
    tcp_path = run_dir / "iperf_tcp.json"
    udp_path = run_dir / "iperf_udp.json"
    ping_path = run_dir / "ping.log"
    cpu_path = run_dir / "cpu.json"
    reconnect_path = run_dir / "reconnect_ms.txt"
    handshake_path = run_dir / "handshake_ms.txt"

    if not meta_path.exists():
        print(f"Skipping {run_dir.name}: missing metadata.json")
        continue

    meta = safe_load_json(meta_path)
    if not meta:
        print(f"Skipping {run_dir.name}: metadata.json unreadable")
        continue

    client_type = detect_client_type(meta)

    tcp = safe_load_json(tcp_path) if tcp_path.exists() else None
    udp = safe_load_json(udp_path) if udp_path.exists() else None

    ping_text = ping_path.read_text(encoding="utf-8", errors="ignore") if ping_path.exists() else ""
    ping_vals = parse_ping_avg(ping_text)

    cpu_avg = None
    cpu_max = None

    if cpu_path.exists():
        try:
            cpu_data = safe_load_json(cpu_path)
            if isinstance(cpu_data, list) and cpu_data:
                cpu_values = []

                for x in cpu_data:
                    if isinstance(x, dict):
                        if "cpu_percent" in x:
                            cpu_values.append(x["cpu_percent"])
                        elif "cpu" in x:
                            cpu_values.append(x["cpu"])

                if cpu_values:
                    cpu_avg = sum(cpu_values) / len(cpu_values)
                    cpu_max = max(cpu_values)
        except Exception:
            pass

    reconnect_ms = None
    if reconnect_path.exists():
        try:
            val = float(reconnect_path.read_text().strip())
            reconnect_ms = val if val >= 0 else None
        except Exception:
            pass

    handshake_ms = None
    if handshake_path.exists():
        try:
            val = float(handshake_path.read_text().strip())
            handshake_ms = val if val >= 0 else None
        except Exception:
            pass

    tcp_bps = extract_iperf_tcp_bits_per_sec(tcp)
    udp_fields = extract_udp_fields(udp)

    tcp_mbps = (tcp_bps / 1_000_000) if tcp_bps else None

    throughput_per_cpu = None
    if tcp_mbps and cpu_avg:
        throughput_per_cpu = tcp_mbps / cpu_avg

    row = {
        "run_id": meta.get("run_id"),
        "stage": meta.get("stage"),
        "vpn": meta.get("vpn"),
        "client_type": client_type,
        "host": meta.get("host"),
        "repeat": meta.get("repeat"),
        "mtu": meta.get("mtu"),
        "delay_ms": meta.get("delay_ms"),
        "loss_pct": meta.get("loss_pct"),
        "cpu_stress": meta.get("cpu_stress"),

        # Performance
        "tcp_throughput_mbps": tcp_mbps,
        "udp_throughput_mbps": (udp_fields["udp_bits_per_sec"] / 1_000_000) if udp_fields["udp_bits_per_sec"] else None,
        "udp_loss_pct_actual": udp_fields["udp_loss_pct"],
        "udp_jitter_ms": udp_fields["udp_jitter_ms"],

        # Latency
        "rtt_avg_ms": ping_vals["rtt_avg_ms"],
        "rtt_mdev_ms": ping_vals["rtt_mdev_ms"],

        # CPU
        "cpu_avg_percent": cpu_avg,
        "cpu_max_percent": cpu_max,

        # Advanced metrics
        "throughput_per_cpu": throughput_per_cpu,
        "reconnect_ms": reconnect_ms,
        "handshake_ms": handshake_ms,

        "folder": str(run_dir),
    }

    rows.append(row)

df = pd.DataFrame(rows)

df.to_csv(OUT_DIR / "results.csv", index=False)

print(f"Saved: {OUT_DIR / 'results.csv'}")
print(f"Total runs processed: {len(df)}")