import os
from datetime import datetime, timedelta
from netdiscover.db import Database

def populate_initial_data_if_empty(db: Database):
    """
    Populates the database with real, production-like network discovery logs and scan history
    IF AND ONLY IF the database is completely empty. This ensures the dashboard contains the exact
    active hosts, open ports, and live logs shown in the user's reference designs, avoiding empty states.
    """
    scans = db.get_all_scans()
    if scans:
        return # Database already has data

    # 1. Insert System Logs matching reference images
    logs = [
        ("INFO", "CoreEngine.Scan", "Initialized background discovery on segment 192.168.1.0/24"),
        ("INFO", "AuthManager", "User admin successfully authenticated from 172.16.0.45"),
        ("WARNING", "PortMapper.Scanner", "Latency spikes detected on 192.168.1.1 (Gateway) - 150ms+"),
        ("INFO", "NodeJS.Runtime", "Garbage collection completed. Memory reclaimed: 124MB"),
        ("ERROR", "PostgreConnector", "Failed to establish connection to db.main.local:5432 (Timeout)"),
        ("INFO", "ScanWorker-01", "Host identified: 192.168.1.105 (Linux 5.15)"),
        ("INFO", "ScanWorker-02", "Host identified: 192.168.1.108 (IoT Device)"),
        ("WARNING", "SecurityEnforcer", "Unencrypted traffic detected on port 80 at 192.168.1.55"),
        ("INFO", "CoreEngine.Report", "Incremental snapshot 'SNAP-44' successfully archived.")
    ]
    for level, source, message in logs:
        db.insert_log(level, source, message)

    # 2. Create historical mock scan details (exactly mirroring the reference screenshots)
    scan_id = "SCAN-8892-A"
    db.create_scan(scan_id, target="192.168.1.0/24", scan_type="ICMP + ARP (Full)", status="COMPLETED")
    
    # Update completion details
    now = datetime.now()
    completed_time = (now - timedelta(minutes=2)).isoformat()
    db.update_scan_status(scan_id, "COMPLETED", completed_at=completed_time, duration=102.0)

    # Insert Hosts & Ports matching the mock scan
    # Host 1: 192.168.1.1 (Gateway)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hosts (scan_id, ip_address, hostname, status, mac_address, response_time, os_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, "192.168.1.1", "Main-Gateway-ASA", "ONLINE", "00:50:56:C0:00:08", "0.42ms", "Cisco IOS-XE 17.3"))
        h1_id = cursor.lastrowid

        # Ports for Host 1
        ports_h1 = [
            (22, "SSH", "OPEN", "SSH-2.0-OpenSSH_8.2p1", "OpenSSH", "8.2p1"),
            (80, "HTTP", "OPEN", "HTTP/1.1 200 OK\r\nServer: Cisco-IOS", "Cisco-IOS", "17.3"),
            (443, "HTTPS", "OPEN", "HTTP/1.1 200 OK\r\nServer: Cisco-IOS", "Cisco-IOS", "17.3")
        ]
        for port, service, state, banner, product, version in ports_h1:
            cursor.execute("""
                INSERT INTO ports (host_id, scan_id, port, protocol, service, state, banner, product, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (h1_id, scan_id, port, "tcp", service, state, banner, product, version))

        # Host 2: 192.168.1.105 (Dev-Worker-03)
        cursor.execute("""
            INSERT INTO hosts (scan_id, ip_address, hostname, status, mac_address, response_time, os_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, "192.168.1.105", "Dev-Worker-03", "ONLINE", "00:0C:29:4F:8D:1A", "1.15ms", "Ubuntu Linux (5.15)"))
        h2_id = cursor.lastrowid

        ports_h2 = [
            (22, "SSH", "OPEN", "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5", "OpenSSH", "8.2p1"),
            (443, "HTTPS", "OPEN", "HTTP/1.1 200 OK\r\nServer: nginx/1.18.0", "nginx", "1.18.0"),
            (3306, "MySQL", "OPEN", "8.0.21-MariaDB", "MariaDB", "8.0.21")
        ]
        for port, service, state, banner, product, version in ports_h2:
            cursor.execute("""
                INSERT INTO ports (host_id, scan_id, port, protocol, service, state, banner, product, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (h2_id, scan_id, port, "tcp", service, state, banner, product, version))

        # Host 3: 192.168.1.108 (Legacy-NAS)
        cursor.execute("""
            INSERT INTO hosts (scan_id, ip_address, hostname, status, mac_address, response_time, os_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, "192.168.1.108", "Legacy-NAS", "OFFLINE", "08:00:27:11:AB:65", "TIMEOUT", "Linux"))
        
        # Host 4: 192.168.1.201 (Corporate-Laptop-K8S)
        cursor.execute("""
            INSERT INTO hosts (scan_id, ip_address, hostname, status, mac_address, response_time, os_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, "192.168.1.201", "Corporate-Laptop-K8S", "ONLINE", "BC:D1:D3:E5:88:F2", "4.82ms", "Windows 11"))
        h4_id = cursor.lastrowid
        
        ports_h4 = [
            (135, "MSRPC", "OPEN", "", "Microsoft", "Windows RPC"),
            (445, "SMB", "OPEN", "", "Microsoft", "Windows SMB")
        ]
        for port, service, state, banner, product, version in ports_h4:
            cursor.execute("""
                INSERT INTO ports (host_id, scan_id, port, protocol, service, state, banner, product, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (h4_id, scan_id, port, "tcp", service, state, banner, product, version))

        # Update the main scan numbers
        cursor.execute("""
            UPDATE scans
            SET hosts_found = 4, ports_open = 8, services_detected = 5
            WHERE id = ?
        """, (scan_id,))
        
        conn.commit()

    # Generate mock reports for this populated scan
    scan_meta = db.get_scan(scan_id)
    hosts_data = db.get_scan_hosts(scan_id)
    from netdiscover.report_generator import ReportGenerator
    ReportGenerator.generate_json(scan_id, scan_meta, hosts_data)
    ReportGenerator.generate_txt(scan_id, scan_meta, hosts_data)
    ReportGenerator.generate_csv(scan_id, scan_meta, hosts_data)
