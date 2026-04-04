# VPN Thesis – Reproducibility Repository

Master's thesis project: Performance and Security Evaluation of WireGuard, OpenVPN and IPsec as Enterprise Remote Access Solutions

&#x20;

This repository contains the scripts, configuration templates, and analysis tools used for a master’s thesis comparing \*\*WireGuard\*\*, \*\*OpenVPN\*\*, and \*\*IPsec (strongSwan)\*\* as enterprise remote access VPN solutions.



## Metrics

The work evaluates:

\- throughput

\- latency / RTT

\- jitter

\- packet loss

\- CPU and memory usage

\- handshake time

\- reconnect time

\- MTU / fragmentation behavior

\- mobility behavior

\- throughput-per-CPU efficiency



\## Testbed summary



The testbed uses:

\- a \*\*CSC cPouta VPS\*\* as the VPN server

\- a \*\*VirtualBox Ubuntu VM\*\* as one client

\- a \*\*Raspberry Pi 4\*\* as another client

\- a \*\*consumer TP-Link router\*\* for NAT and wireless access



\## Repository contents



\- `scripts/`  

&#x20; Automation scripts for running the staged experiment matrix and collecting results.



\- `configs/`  

&#x20; Sanitized configuration templates for WireGuard, OpenVPN, and IPsec.



\- `analysis scripts/`  

&#x20; Python scripts for extracting, aggregating, and plotting results.



\- `README.md`  

&#x20; Reproducibility instructions and repository overview.



\## Experimental stages



The measurement plan includes:

\- Baseline

\- Latency

\- Packet loss

\- MTU variation

\- CPU stress

\- Mobility / reconnect



Each run creates a unique output folder containing:

\- `metadata.json`

\- `ping.log`

\- `iperf\_tcp.json`

\- `iperf\_udp.json`

\- `cpu.json`

\- `capture.pcap`

\- `handshake\_ms.txt`

\- `reconnect\_ms.txt`

\- protocol state snapshots



\## Reproducibility workflow



1\. Prepare the server and clients.

2\. Install VPN software and measurement tools.

3\. Run the staged matrix scripts.

4\. Extract results into CSV format.

5\. Aggregate the measurements.

6\. Generate thesis figures from the outputs.



\## Notes



\- This repository contains \*\*sanitized\*\* templates only.

\- Private keys, secrets, and large raw measurement archives are excluded.

\- Large raw outputs should be stored separately from the Git repository.



\## Expected usage



The repository is intended to support:

\- thesis reproducibility

\- experiment reruns

\- result verification

\- future extension of the methodology

