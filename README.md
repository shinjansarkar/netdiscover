# NetDiscover 🔍

NetDiscover is a production-quality, lightweight, Nmap-inspired network scanner and service enumerator written in Python. It features a modern, responsive dark-themed Flask dashboard to run, visualize, and export audits.

---

## Features
- **Host Discovery**: Multithreaded host detection on a target subnet utilizing **ICMP Echo Pings** (works without root) and **ARP Broadcasts** (requires elevated capabilities).
- **Service & Port Scanning**: Rapid TCP port connection sweeps using a configurable `ThreadPoolExecutor` worker pool.
- **Service Version Detection & Banner Grabbing**: Connects to open ports to read banners and maps protocols with version markers.
- **Database Logs & History**: Maintains scan history, host inventories, and log events in SQLite.
- **Reports Export**: Instant downloads of audits in **TXT**, **JSON**, and **CSV** formats.
- **Interactive Visuals**: Includes live CLI-style consoles and dynamic SVG subnet topology mapping.
- **Docker Support**: Ready to build and run out-of-the-box.

---

## Project Architecture

```
NetDiscover/
├── netdiscover/
│   ├── __init__.py
│   ├── app.py                 # Flask server routes & API endpoints
│   ├── config.py              # Configuration manager (ports, timeouts, threads)
│   ├── db.py                  # SQLite database wrapper & audit logs
│   ├── host_discovery.py      # ICMP & ARP subnet sweeps (ThreadPoolExecutor)
│   ├── port_scanner.py        # TCP socket connect scanner
│   ├── service_detector.py    # Banner regex parser & service mapper
│   ├── banner_grabber.py      # Socket payload query tool
│   ├── report_generator.py    # Exporters (JSON, TXT, CSV)
│   ├── scanner_engine.py      # Core scan pipeline orchestrator
│   ├── init_helper.py         # Database pre-population helper
│   └── templates/             # Jinja2 Dashboard Layouts
│       ├── base.html
│       ├── index.html
│       ├── new_scan.html
│       ├── scan_history.html
│       ├── reports.html
│       └── logs.html
├── run.py                     # Entry start script
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Compose stack specification
├── requirements.txt           # Python dependency manifest
└── README.md                  # System instruction handbook
```

---

## Installation & Setup

### 1. Virtual Environment Setup

#### Create & Activate Virtual Environment

**Linux / macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Deactivate Virtual Environment
When done working, deactivate the venv:
```bash
deactivate
```

---

### 2. Local Setup (Standard Host Execution)

Ensure python3 and pip are installed. Install system networking tools first:

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y iputils-ping net-tools libpcap-dev gcc

# macOS (using Homebrew)
brew install tcpdump libpcap
```

Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Launch the server:
```bash
python run.py
```
Open **`http://localhost:5000`** in your browser.

> [!NOTE]
> ICMP Ping and Port Scanning run as standard users. To execute Scapy ARP scanning, run the Python program with elevated root privileges:
> ```bash
> sudo ./venv/bin/python run.py
> ```
> Alternatively, on Linux, grant capabilities to Python:
> ```bash
> sudo setcap cap_net_raw=ep $(which python3)
> ```

---

### 3. Running in Docker

#### Understanding the Dockerfile

The `Dockerfile` defines the container image:

```dockerfile
# Use official lightweight Python image
FROM python:3.10-slim

# Install system dependencies needed for network commands and scapy
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    net-tools \
    tcpdump \
    libpcap-dev \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY netdiscover/ ./netdiscover/
COPY run.py .

# Expose port for dashboard
EXPOSE 5000

# Run Flask server
CMD ["python", "run.py"]
```

**Dockerfile Breakdown:**
- **`FROM python:3.10-slim`** — Starts with lightweight Python 3.10 image
- **`RUN apt-get...`** — Installs networking tools (ping, tcpdump, libpcap) for scanning
- **`WORKDIR /app`** — Sets container working directory
- **`COPY requirements.txt...`** — Copies and installs Python dependencies
- **`COPY netdiscover/...`** — Copies application source code
- **`EXPOSE 5000`** — Documents that container listens on port 5000
- **`CMD`** — Runs the Flask app on startup

#### Build & Run with Docker Compose

Docker Compose automates image building and container orchestration:

```bash
# Build and start container (with live reload)
docker-compose up --build

# Start without rebuilding
docker-compose up

# Run in background (detached)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

The dashboard is accessible on **`http://localhost:5000`**.

#### Manual Docker Build & Run

If you prefer building without Docker Compose:

```bash
# Build image
docker build -t netdiscover:latest .

# Run container
docker run --network host -p 5000:5000 netdiscover:latest
```

> [!IMPORTANT]
> The Docker setup uses `network_mode: host` (in docker-compose.yml) to allow raw socket communication and ARP broadcasts on the host's actual network interfaces. This enables full scanning capabilities within the container.

---

## Core Networking Concepts Used

### 1. Subnetting & CIDR Notation
NetDiscover parses subnets in CIDR notation (e.g., `192.168.1.0/24`). A `/24` subnet masks 24 bits for the network, providing 254 usable host addresses (`.1` to `.254`).

### 2. ICMP Echo Request (Ping)
Pings transmit an ICMP Type 8 packet. If the host is online, it replies with an ICMP Type 0 (Echo Reply). NetDiscover utilizes the system's native `ping` binary to execute this test reliably without root privileges.

### 3. ARP Broadcast (Address Resolution Protocol)
ARP resolves IP addresses to physical MAC addresses. The scanner broadcasts an ARP request (`Who has 192.168.1.X? Tell 192.168.1.Y`) to the MAC address `ff:ff:ff:ff:ff:ff`. Active hosts reply directly.

### 4. TCP Connect Port Scan
The scanner initiates a full 3-way handshake (`SYN` -> `SYN-ACK` -> `ACK`) using standard socket connections. This guarantees accuracy without requiring raw socket capabilities.

### 5. Banner Grabbing & Service Fingerprinting
Once a port connects, the application captures initial application greetings (e.g., `SSH-2.0-OpenSSH_8.2p1`). By parsing these greetings using regular expressions, NetDiscover extracts specific service versions (like NGINX, Apache, MariaDB).
