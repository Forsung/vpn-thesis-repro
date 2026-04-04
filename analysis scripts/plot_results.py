from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
IN_FILE = Path(r"C:\vpn-thesis\analysis\outputs\aggregated.csv")
FIG_DIR = Path(r"C:\vpn-thesis\analysis\figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(IN_FILE)

sns.set_theme(style="whitegrid")


# -------------------------------
# HELPER: BAR PLOT WITH VALUES
# -------------------------------
def barplot_with_labels(data, x, y, hue, title, ylabel, filename):
    plt.figure(figsize=(10, 6))

    ax = sns.barplot(
        data=data,
        x=x,
        y=y,
        hue=hue,
        errorbar="sd"
    )

    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3)

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(x)
    plt.tight_layout()

    plt.savefig(FIG_DIR / f"{filename}.pdf")  # VECTOR FORMAT
    plt.close()


# -------------------------------
# FILTER HELPERS
# -------------------------------
baseline = df[df["stage"] == "baseline"]
latency = df[df["stage"] == "latency"]
loss = df[df["stage"] == "loss"]
mtu = df[df["stage"] == "mtu"]
cpu_stress = df[df["stage"] == "cpu_stress"]
mobility = df[df["stage"] == "mobility"]


# ===============================
# 1. BASELINE PERFORMANCE
# ===============================

barplot_with_labels(
    baseline,
    x="vpn",
    y="tcp_throughput_mean",
    hue="client_type",
    title="Baseline TCP Throughput",
    ylabel="Throughput (Mbps)",
    filename="baseline_throughput"
)

barplot_with_labels(
    baseline,
    x="vpn",
    y="rtt_mean",
    hue="client_type",
    title="Baseline RTT",
    ylabel="RTT (ms)",
    filename="baseline_rtt"
)

barplot_with_labels(
    baseline,
    x="vpn",
    y="cpu_mean",
    hue="client_type",
    title="Baseline CPU Usage",
    ylabel="CPU (%)",
    filename="baseline_cpu"
)

barplot_with_labels(
    baseline,
    x="vpn",
    y="efficiency_mean",
    hue="client_type",
    title="Throughput per CPU Efficiency",
    ylabel="Mbps per %CPU",
    filename="baseline_efficiency"
)


# ===============================
# 2. LATENCY IMPACT
# ===============================

barplot_with_labels(
    latency,
    x="vpn",
    y="tcp_throughput_mean",
    hue="client_type",
    title="Throughput under 50 ms Latency",
    ylabel="Throughput (Mbps)",
    filename="latency_throughput"
)

barplot_with_labels(
    latency,
    x="vpn",
    y="rtt_mean",
    hue="client_type",
    title="RTT under Latency",
    ylabel="RTT (ms)",
    filename="latency_rtt"
)


# ===============================
# 3. PACKET LOSS IMPACT
# ===============================

barplot_with_labels(
    loss,
    x="vpn",
    y="tcp_throughput_mean",
    hue="client_type",
    title="Throughput under 1% Packet Loss",
    ylabel="Throughput (Mbps)",
    filename="loss_throughput"
)

barplot_with_labels(
    loss,
    x="vpn",
    y="rtt_mean",
    hue="client_type",
    title="RTT under Packet Loss",
    ylabel="RTT (ms)",
    filename="loss_rtt"
)


# ===============================
# 4. MTU EFFECTS
# ===============================

barplot_with_labels(
    mtu,
    x="vpn",
    y="tcp_throughput_mean",
    hue="client_type",
    title="Throughput under MTU Variation",
    ylabel="Throughput (Mbps)",
    filename="mtu_throughput"
)


# ===============================
# 5. CPU STRESS
# ===============================

barplot_with_labels(
    cpu_stress,
    x="vpn",
    y="tcp_throughput_mean",
    hue="client_type",
    title="Throughput under CPU Stress",
    ylabel="Throughput (Mbps)",
    filename="cpu_stress_throughput"
)

barplot_with_labels(
    cpu_stress,
    x="vpn",
    y="cpu_mean",
    hue="client_type",
    title="CPU Usage under Stress",
    ylabel="CPU (%)",
    filename="cpu_stress_cpu"
)


# ===============================
# 6. MOBILITY (SECURITY + STABILITY)
# ===============================

barplot_with_labels(
    mobility,
    x="vpn",
    y="reconnect_mean",
    hue="client_type",
    title="Reconnect Time (Mobility)",
    ylabel="Time (ms)",
    filename="mobility_reconnect"
)

barplot_with_labels(
    mobility,
    x="vpn",
    y="handshake_mean",
    hue="client_type",
    title="Handshake Time",
    ylabel="Time (ms)",
    filename="mobility_handshake"
)


print(f"All figures saved to: {FIG_DIR}")