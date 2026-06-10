import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from netdiscover.config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    """
    SQLite Database Manager for NetDiscover.
    Handles storage of scans, discovered hosts, open ports, and system logs.
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """
        Establishes a connection to the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """
        Initializes the database schema if it doesn't already exist.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Scans Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id TEXT PRIMARY KEY,
                    target TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    hosts_found INTEGER DEFAULT 0,
                    ports_open INTEGER DEFAULT 0,
                    services_detected INTEGER DEFAULT 0,
                    duration REAL DEFAULT 0.0
                )
            """)

            # 2. Hosts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hosts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    hostname TEXT DEFAULT 'Unknown',
                    status TEXT NOT NULL,
                    mac_address TEXT DEFAULT 'Unknown',
                    response_time TEXT DEFAULT '0ms',
                    os_detected TEXT DEFAULT 'Unknown',
                    FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
                )
            """)

            # 3. Ports Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host_id INTEGER NOT NULL,
                    scan_id TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    protocol TEXT DEFAULT 'tcp',
                    service TEXT DEFAULT 'Unknown',
                    state TEXT NOT NULL,
                    banner TEXT,
                    product TEXT DEFAULT 'Unknown',
                    version TEXT DEFAULT 'Unknown',
                    FOREIGN KEY (host_id) REFERENCES hosts (id) ON DELETE CASCADE,
                    FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
                )
            """)

            # 4. Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully.")

    # --- Log Management ---
    def insert_log(self, level: str, source: str, message: str):
        """
        Inserts a system log into the database.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO system_logs (level, source, message) VALUES (?, ?, ?)",
                    (level, source, message)
                )
                conn.commit()
        except Exception as e:
            # Print to standard print, since database logger might fail recursively
            print(f"Error inserting log: {str(e)}")

    def get_logs(self, limit: int = 100, level: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves logs from the database, optionally filtered by level.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if level:
                cursor.execute(
                    "SELECT timestamp, level, source, message FROM system_logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?",
                    (level.upper(), limit)
                )
            else:
                cursor.execute(
                    "SELECT timestamp, level, source, message FROM system_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # --- Scan Management ---
    def create_scan(self, scan_id: str, target: str, scan_type: str, status: str = "RUNNING") -> str:
        """
        Creates a new scan record and logs the event.
        """
        created_at = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO scans (id, target, scan_type, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (scan_id, target, scan_type, status, created_at)
            )
            conn.commit()
        self.insert_log("INFO", "ScanEngine", f"Scan {scan_id} initialized for target {target} ({scan_type})")
        return scan_id

    def update_scan_status(self, scan_id: str, status: str, completed_at: str = None, duration: float = 0.0):
        """
        Updates the scan state (e.g. COMPLETED or FAILED) and records details.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if completed_at:
                cursor.execute(
                    "UPDATE scans SET status = ?, completed_at = ?, duration = ? WHERE id = ?",
                    (status, completed_at, duration, scan_id)
                )
            else:
                cursor.execute(
                    "UPDATE scans SET status = ? WHERE id = ?",
                    (status, scan_id)
                )
            conn.commit()
        self.insert_log("INFO", "ScanEngine", f"Scan {scan_id} status updated to {status}")

    def save_scan_results(self, scan_id: str, results: List[Dict[str, Any]], duration: float):
        """
        Saves all discovered hosts and open ports to the database.
        Calculates aggregate stats and updates the scans table.
        """
        completed_at = datetime.now().isoformat()
        hosts_found = len(results)
        ports_open = 0
        services_detected = set()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for host_data in results:
                # Insert host
                cursor.execute("""
                    INSERT INTO hosts (scan_id, ip_address, hostname, status, mac_address, response_time, os_detected)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_id,
                    host_data["ip"],
                    host_data["hostname"],
                    host_data["status"],
                    host_data.get("mac", "Unknown"),
                    host_data.get("response_time", "0ms"),
                    host_data.get("os", "Unknown")
                ))
                host_id = cursor.lastrowid
                
                # Insert open ports
                for port_data in host_data.get("ports", []):
                    ports_open += 1
                    if port_data["service"] and port_data["service"] != "Unknown":
                        services_detected.add(port_data["service"])
                        
                    cursor.execute("""
                        INSERT INTO ports (host_id, scan_id, port, protocol, service, state, banner, product, version)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        host_id,
                        scan_id,
                        port_data["port"],
                        "tcp",
                        port_data["service"],
                        port_data["state"],
                        port_data.get("banner"),
                        port_data.get("product", "Unknown"),
                        port_data.get("version", "Unknown")
                    ))
            
            # Update scan record with completed stats
            cursor.execute("""
                UPDATE scans 
                SET status = 'COMPLETED', completed_at = ?, duration = ?, hosts_found = ?, ports_open = ?, services_detected = ?
                WHERE id = ?
            """, (completed_at, duration, hosts_found, ports_open, len(services_detected), scan_id))
            
            conn.commit()

        self.insert_log("INFO", "ScanEngine", f"Scan {scan_id} saved: {hosts_found} hosts found, {ports_open} open ports.")

    # --- Query API ---
    def get_all_scans(self) -> List[Dict[str, Any]]:
        """
        Fetches all scans in reverse chronological order.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches details of a specific scan.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_scan_hosts(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Fetches all hosts discovered in a specific scan.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hosts WHERE scan_id = ? ORDER BY ip_address", (scan_id,))
            hosts_rows = [dict(row) for row in cursor.fetchall()]
            
            # Attach ports to each host
            for host in hosts_rows:
                cursor.execute("SELECT * FROM ports WHERE host_id = ? ORDER BY port", (host["id"],))
                host["ports"] = [dict(p) for p in cursor.fetchall()]
                
            return hosts_rows

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Computes aggregate dashboard statistics.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total scan executions
            cursor.execute("SELECT COUNT(*) FROM scans")
            total_scans = cursor.fetchone()[0]
            
            # Unique active hosts ever found
            cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM hosts WHERE status = 'ONLINE'")
            total_active_hosts = cursor.fetchone()[0]
            
            # Unique ports found open
            cursor.execute("SELECT COUNT(*) FROM ports WHERE state = 'OPEN'")
            total_open_ports = cursor.fetchone()[0]
            
            # Unique services identified
            cursor.execute("SELECT COUNT(DISTINCT service) FROM ports WHERE service != 'Unknown'")
            total_services = cursor.fetchone()[0]
            
            # Last scan duration and ID
            cursor.execute("SELECT duration, completed_at FROM scans WHERE status = 'COMPLETED' ORDER BY created_at DESC LIMIT 1")
            last_scan_row = cursor.fetchone()
            
            last_duration = 0.0
            if last_scan_row:
                last_duration = last_scan_row[0]

            return {
                "total_scans": total_scans,
                "active_hosts": total_active_hosts,
                "open_ports": total_open_ports,
                "services_identified": total_services,
                "last_scan_duration": f"{int(last_duration)}s" if last_duration < 60 else f"{int(last_duration // 60)}m {int(last_duration % 60)}s"
            }
            
    def clear_database(self):
        """
        Clears all tables (used for testing or resetting).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ports")
            cursor.execute("DELETE FROM hosts")
            cursor.execute("DELETE FROM scans")
            cursor.execute("DELETE FROM system_logs")
            conn.commit()
        self.insert_log("WARNING", "Database", "Database has been reset.")
