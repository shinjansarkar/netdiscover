# NetDiscover: Project Description & Technical Overview

NetDiscover is a lightweight, web-based, Nmap-inspired network discovery and service auditing application. Built with Python, Flask, and SQLite, it offers a high-performance scanning engine alongside a premium, responsive dark-themed dashboard.

---

## 👥 Who This Project Helps

This project provides distinct value to both everyday tech enthusiasts and professional IT practitioners.

### 1. How It Helps an IT / Security Professional
* **Subnet Mapping & Asset Inventory**: IT teams can scan subnet blocks (e.g., `192.168.1.0/24`) to discover active hosts, resolve their hostnames via reverse DNS, and map their physical MAC addresses.
* **Security & Vulnerability Auditing**: Captures server banners (e.g., `SSH-2.0-OpenSSH_8.2p1`) to pinpoint exactly what software and version is running on open ports, allowing administrators to find outdated, unpatched, or unauthorized services.
* **Port Availability Monitoring**: Identifies open ports across common TCP services, exposing firewall configuration errors.
* **Compliance & Reporting**: Logs and stores all scans in an SQLite database. It automatically generates exportable audit reports in **CSV**, **JSON**, and **TXT** formats.
* **Non-Root & Elevated Modes**: Allows ICMP-based scanning without requiring high-level root privileges, or uses elevated capabilities for ARP packet sweeps using Scapy.

### 2. How It Helps an Everyday Person / Student
* **Home Network Security**: Allows users to check which devices are connected to their home Wi-Fi or LAN, helping identify intruders, leaks, or unrecognized smart-home (IoT) gadgets.
* **No Complex Command Line**: Instead of memorizing hundreds of command-line switches for tools like `nmap` or `arping`, users can configure and trigger scans via a clean browser UI.
* **Educational Value**: Helps students learn core network concepts like CIDR notation, ICMP protocols, Address Resolution Protocol (ARP), TCP handshakes, and banner fingerprinting.

---

## 💡 The Main Idea of NetDiscover

The core philosophy of NetDiscover is **simplicity, speed, and visibility**. 

It serves as a bridge between powerful but complex CLI networking utilities and a user-friendly, responsive web application. The main goal is to let administrators input a network scope, parallelize discovery using multithreading, automatically audit running service versions, and present the results in an interactive dashboard complete with live logs and structured exports.

---

## ⚙️ How It Works (Step-by-Step)

The scanner execution proceeds through five sequential steps:

```
+------------------------------------------+
|  Configure Target Subnet & Port Range    |
+------------------------------------------+
                     |
                     v
+------------------------------------------+
|       1. Host Discovery Phase           |
|  (ICMP Ping Sweep or ARP Scapy Sweep)    |
+------------------------------------------+
                     |
                     v
+------------------------------------------+
|       2. Port Scanning Phase             |
|   (Multithreaded TCP Connect Sweep)      |
+------------------------------------------+
                     |
                     v
+------------------------------------------+
|  3. Banner Grabbing & Service Detection  |
|   (Socket banner grab & regex mapping)   |
+------------------------------------------+
                     |
                     v
+------------------------------------------+
|   4. DB Logging & Report Generation      |
|  (SQLite DB insert & CSV/JSON/TXT files) |
+------------------------------------------+
                     |
                     v
+------------------------------------------+
|       5. View Dashboard Results          |
+------------------------------------------+
```

### 1. Configuration & Scope Input
* The user inputs a target network scope (e.g. `10.0.0.0/24`) in the web interface.
* They choose a port scope (e.g., Common Ports, Top 100, Top 1000, or custom ranges like `22, 80, 8000-8080`).
* They select the discovery mechanism (**ICMP** or **ARP**), thread pool capacity, and hit **Start Scan**.

### 2. Host Discovery Phase
The system initiates a background thread (`ScannerEngine.launch_scan_async`) and deploys a multithreaded network sweep:
* **ICMP Ping Sweep**: For environments running standard privileges, the tool uses standard Python subprocesses to execute cross-platform `ping` commands. Active hosts are marked **ONLINE**.
* **ARP Sweep**: If run with root privileges on Linux, NetDiscover uses Scapy to broadcast ARP frames (`Who has IP X? Tell Y`) to the MAC address `ff:ff:ff:ff:ff:ff`. This resolves MAC addresses and bypasses local host-based firewalls that ignore ICMP packets.
* **Reverse DNS Lookup**: Resolves active IP addresses to hostnames.

### 3. TCP Port Scanning Phase
* For each host confirmed to be online, the scanner spins up a `ThreadPoolExecutor` worker pool.
* It performs a TCP connect scan (`connect_ex`) to simulate a full three-way handshake (`SYN` -> `SYN-ACK` -> `ACK`). This measures service accessibility reliably on standard user levels.

### 4. Banner Grabbing & Service Fingerprinting
* Once a port registers as `OPEN`, the engine attempts to grab its application banner (`BannerGrabber.grab`):
  * For protocols that speak first (e.g., SSH, FTP, SMTP), it grabs the welcome banner immediately.
  * For silent protocols (e.g., HTTP/HTTPS), it sends a generic payload (like `GET / HTTP/1.1`) to prompt a header response.
* The banner is passed to `ServiceDetector.detect`, which runs regular expressions to parse out the product name (e.g., Apache, NGINX, vsFTPd, OpenSSH) and version numbers.

### 5. Logging, Archiving & Reporting
* **Persistent Audit History**: The Flask application writes records to `netdiscover.db` using an SQLite connector (`Database` class).
* **Format Exporters**: The scanner saves three report formats to disk inside the `reports/` folder:
  1. `.csv` — For spreadsheet import and data sorting.
  2. `.json` — For developer integration and API ingestion.
  3. `.txt` — For human-readable CLI-style logging.
* **Live Progress**: An in-memory monitor tracking progress (`ACTIVE_SCANS`) pushes updates to the frontend dashboard.

---

## 🛠️ Project Core Architecture

Here is how the modules in the codebase work together:

| Module | Purpose | Key Technologies |
| :--- | :--- | :--- |
| **`run.py`** | Server entry point. | Python, Flask, gevent / WSGI |
| **`app.py`** | Web controller handling routing, API controllers, and page renders. | Jinja2 templates, Flask |
| **`scanner_engine.py`** | Core pipeline orchestrator. Manages thread transitions & database logging. | Python `threading`, `uuid` |
| **`host_discovery.py`** | Identifies live targets using network probes. | `subprocess` (Ping), Scapy (ARP) |
| **`port_scanner.py`** | Scans TCP ports in parallel. | `socket`, `ThreadPoolExecutor` |
| **`banner_grabber.py`**| Grabs port response banners. | TCP socket streams |
| **`service_detector.py`**| Parses version signatures via regex. | Regular Expressions (`re`) |
| **`db.py`** | Persists scan configurations, logs, and findings. | SQLite3 |
| **`report_generator.py`**| Generates CSV, JSON, and plain text files. | `csv`, `json` |

---

## ⚡ Core Networking Concepts Implemented

1. **Classless Inter-Domain Routing (CIDR)**: Subnetting parsing allowing variable-length masks (e.g. `/24` representing 256 addresses, `/30` representing 4 addresses).
2. **Address Resolution Protocol (ARP)**: Mapping IP addresses to physical MAC addresses on layer 2 (Ethernet) of the OSI model.
3. **Internet Control Message Protocol (ICMP)**: Utilizes ping packets (Type 8 Echo Request / Type 0 Echo Reply) on Layer 3 of the OSI model.
4. **TCP 3-Way Handshake**: Port scanning simulates standard client-server socket negotiation.
5. **Banner Fingerprinting**: Service profiling based on text responses from active server sockets.
