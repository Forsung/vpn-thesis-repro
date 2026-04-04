from pathlib import Path
import pandas as pd

IN_FILE = Path(r"C:\vpn-thesis\analysis\outputs\results.csv")
OUT_FILE = Path(r"C:\vpn-thesis\analysis\outputs\aggregated.csv")

df = pd.read_csv(IN_FILE)

# -------------------------------
# CLEAN DATA (important)
# -------------------------------

# Ensure numeric columns are correct
numeric_cols = [
    "tcp_throughput_mbps",
    "udp_throughput_mbps",
    "rtt_avg_ms",
    "rtt_mdev_ms",
    "cpu_avg_percent",
    "reconnect_ms",
    "handshake_ms",
    "throughput_per_cpu",
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------------
# GROUPING (VERY IMPORTANT FIX)
# -------------------------------

group_cols = [
    "vpn",
    "client_type",   # ✅ replaces host
    "stage",
    "mtu",
    "delay_ms",
    "loss_pct",
    "cpu_stress",
]

# -------------------------------
# AGGREGATION (THESIS METRICS)
# -------------------------------

agg = df.groupby(group_cols, dropna=False).agg(

    # Throughput
    tcp_throughput_mean=("tcp_throughput_mbps", "mean"),
    tcp_throughput_std=("tcp_throughput_mbps", "std"),

    udp_throughput_mean=("udp_throughput_mbps", "mean"),
    udp_throughput_std=("udp_throughput_mbps", "std"),

    # Latency
    rtt_mean=("rtt_avg_ms", "mean"),
    rtt_std=("rtt_avg_ms", "std"),

    jitter_mean=("rtt_mdev_ms", "mean"),

    # CPU
    cpu_mean=("cpu_avg_percent", "mean"),
    cpu_std=("cpu_avg_percent", "std"),

    # Efficiency (NEW)
    efficiency_mean=("throughput_per_cpu", "mean"),
    efficiency_std=("throughput_per_cpu", "std"),

    # Reliability
    reconnect_mean=("reconnect_ms", "mean"),
    reconnect_std=("reconnect_ms", "std"),

    handshake_mean=("handshake_ms", "mean"),
    handshake_std=("handshake_ms", "std"),

    # Sample count (VERY IMPORTANT for thesis)
    samples=("tcp_throughput_mbps", "count"),

).reset_index()

# -------------------------------
# ROUND VALUES (for thesis tables)
# -------------------------------

round_cols = [
    "tcp_throughput_mean", "tcp_throughput_std",
    "udp_throughput_mean", "udp_throughput_std",
    "rtt_mean", "rtt_std",
    "jitter_mean",
    "cpu_mean", "cpu_std",
    "efficiency_mean", "efficiency_std",
    "reconnect_mean", "reconnect_std",
    "handshake_mean", "handshake_std"
]

for col in round_cols:
    if col in agg.columns:
        agg[col] = agg[col].round(2)

# -------------------------------
# SAVE
# -------------------------------

agg.to_csv(OUT_FILE, index=False)

print(f"Saved: {OUT_FILE}")
print(f"Rows: {len(agg)}")