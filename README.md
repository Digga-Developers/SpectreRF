# SpectreRF

A real-time wireless telemetry pipeline designed to capture, parse, stream, store, and visualize 802.11 management frames. Built for cybersecurity analysis, foot traffic modeling, probe tracking, and wireless threat detection (such as deauthentication floods).

---

## Features

- **Non-Disruptive Real-Time Sniffing:** Creates a dedicated virtual monitor interface (`mon0`) inside Docker, leaving host Wi-Fi connectivity fully operational.
- **802.11 Frame Ingestion:** Captures management frames (Beacons, Probe Requests, Deauthentications) using Scapy.
- **Time-Series Storage:** High-performance storage using **TimescaleDB** (PostgreSQL extension) with hypertables optimized for high-frequency telemetry data.
- **SOC Dashboarding:** Fully provisioned **Grafana** dashboard tracking real-time device density, sticky clients, probe requests, and security alerts.
- **Key Use Cases:**
  - *Foot Traffic & Occupancy Modeling:* Monitor spatial and temporal device density trends.
  - *Probe Tracking / Sticky Client Analysis:* Inspect plaintext probe requests to identify nearby network probes.
  - *Deauthentication Detection:* Catch unencrypted deauth flood attacks targeting specific BSSIDs.

---

## Tech Stack

- **Language:** Python 3.12+ (managed with `uv`)
- **Packet Capture:** Scapy, `libpcap`, `nl80211`
- **Database:** TimescaleDB (PostgreSQL)
- **Visualization:** Grafana
- **Containerization:** Docker & Docker Compose

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
├── docker-compose.yml                  # Full stack orchestration (DB, Grafana, Sniffer)
├── Dockerfile                          # Multi-stage Alpine container for SpectreRF
├── entrypoint.sh                       # Non-intrusive mon0 virtual interface creation script
├── .env                                # Environment variables (DB credentials, interface name)
├── .gitignore
├── README.md
├── requirements.txt
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

To capture 802.11 frames safely without disrupting your primary wireless interface—which can cause state mismatches and system hangs—it is recommended to create a **virtual monitor interface** rather than modifying your physical card directly.

Determine what your physical wireless interface name is:

```bash
iw dev
```

Look where it says "Interface \<name\>"

Replace `wlan0` with your actual physical wireless interface name:

```bash
# Create a virtual monitor interface named mon0 on top of your physical card
sudo iw dev wlan0 interface add mon0 type monitor

# Bring the virtual monitor interface up
sudo ip link set mon0 up

```

When you are finished capturing, you can clean up and remove the virtual interface without affecting your primary connection:

```bash
sudo ip link set mon0 down
sudo iw dev mon0 del

```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wifi_telemetry
DB_USER=postgres
DB_PASSWORD=password
WIRELESS_INTERFACE=wlan0 # REPLACE with actual interface name

```

### 3. Start Infrastructure (Docker Compose)

**NOTE:** Spinning up this docker container will handle the creation of the virtual montior

Build docker container:

```bash
docker compose build spectrerf --no-cache
```

Spin up TimescaleDB and Grafana:

```bash
docker compose up -d
```

(alternatively in one command: `docker compose up --build -d`)

To shutdown docker container when finished:

```bash
docker compose down
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
