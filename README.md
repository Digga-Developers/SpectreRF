# SpectreRF

A real-time wireless telemetry pipeline designed to capture, parse, stream, store, and visualize 802.11 management frames. Built for cybersecurity analysis, foot traffic modeling, probe tracking, and wireless threat detection (such as deauthentication floods).

---

## Features

* **Real-Time Packet Sniffing:** Captures 802.11 management frames (Beacons, Probe Requests, Deauths) using a wireless network card in monitor mode via Scapy.
* **Time-Series Storage:** High-performance storage using **TimescaleDB** (PostgreSQL extension) with hypertables optimized for high-frequency telemetry data.
* **SOC Dashboarding:** Fully provisioned **Grafana** dashboard tracking real-time device density, sticky clients, probe requests, and security alerts.
* **Key Use Cases:**
* *Foot Traffic & Occupancy Modeling:* Monitor spatial and temporal device density trends.
* *Probe Tracking / Sticky Client Analysis:* Inspect plaintext probe requests to identify nearby network probes.
* *Deauthentication Detection:* Catch unencrypted deauth flood attacks targeting specific BSSIDs.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Packet Capture:** Scapy
* **Database:** TimescaleDB (PostgreSQL)
* **Visualization:** Grafana
* **Containerization:** Docker & Docker Compose

---

## Project Structure

```text
SpectreRF/
├── config                              # Configuration files
│   └── grafana
│       └── provisioning
│           ├── dashboard
│           │   └── dashboards.yaml
│           └── datasources
│               └── datasource.yaml
├── dashboards                          # Exported Grafana JSON dashboard templates     
│   └── soc_overview.json   
├── database                            # Database initialization and schemas
│   └── init.sql                        # TimescaleDB hypertables, indexes, and retention policies
├── docker-compose.yaml                 # Orchestrates TimescaleDB and Grafana
├── .env                                # Environment variables (DB credentials, interface name)
├── .gitignore
├── README.md
└── src                                 # Core application source code
    ├── capture.py                      # Scapy packet sniffer and frame parser
    ├── db.py                           # TimescaleDB connection and bulk inserter worker
    ├── __init__.py
    ├── main.py                         # Entry point orchestrating capture and insertion
    └── models.py                       # Data classes / parsers for 802.11 frames


```

---

## Prerequisites & Setup

### 1. Wireless Card Monitor Mode

To capture 802.11 frames, your wireless card must support monitor mode. Replace `wlan0` with your actual wireless interface name:

```bash
sudo ip link set wlan0 down
sudo iw wlan0 set type monitor
sudo ip link set wlan0 up

```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wifi_telemetry
DB_USER=postgres
DB_PASSWORD=secretpassword
WIRELESS_INTERFACE=wlan0

```

### 3. Start Infrastructure (Docker Compose)

Spin up TimescaleDB and Grafana:

```bash
docker-compose up -d

```

### 4. Run the Telemetry Ingestion Pipeline

Install Python dependencies and run the sniffer:

```bash
uv pip install -r requirements.txt
sudo python -m src/main

```

*(Note: `sudo` or root privileges are typically required to access network interfaces in monitor mode).*

---

## Grafana Dashboard

Once the pipeline is running:

1. Open Grafana in your browser at `http://localhost:3000`.
2. Log in (default credentials are usually `admin` / `admin`).
3. Navigate to dashboards to view the **SOC Overview** tracking frame rates, top probed SSIDs, and anomaly alerts.

---

## License

This project is for educational and authorized defensive cybersecurity research purposes only. Only capture wireless traffic on networks and devices you own or have explicit permission to monitor.
