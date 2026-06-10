import uuid
import time
import logging
import threading
from typing import List, Dict, Any, Optional
from netdiscover.db import Database
from netdiscover.host_discovery import HostDiscovery
from netdiscover.port_scanner import PortScanner
from netdiscover.report_generator import ReportGenerator
from netdiscover.config import COMMON_PORTS, TOP_100_PORTS, TOP_1000_PORTS

logger = logging.getLogger(__name__)

# In-memory progress tracker for active scans
ACTIVE_SCANS: Dict[str, Dict[str, Any]] = {}

class ScannerEngine:
    """
    Core engine that coordinates host discovery, port scanning, service detection,
    database storage, and reporting. Supports asynchronous execution.
    """

    def __init__(self, db: Database = None):
        self.db = db or Database()

    def get_ports_by_range_type(self, range_type: str, custom_ports: str = None) -> List[int]:
        """
        Translates a port range name or custom ports string into a list of integers.
        """
        if range_type == "common":
            return COMMON_PORTS
        elif range_type == "top100":
            return TOP_100_PORTS
        elif range_type == "top1000":
            return TOP_1000_PORTS
        elif range_type == "custom" and custom_ports:
            ports = []
            # Parse custom comma-separated list or ranges
            # Example: "80, 443, 8000-8080"
            for part in custom_ports.split(','):
                part = part.strip()
                if '-' in part:
                    try:
                        start, end = map(int, part.split('-'))
                        ports.extend(range(start, end + 1))
                    except ValueError:
                        logger.error(f"Invalid custom port range segment: {part}")
                else:
                    try:
                        ports.append(int(part))
                    except ValueError:
                        logger.error(f"Invalid custom port integer: {part}")
            # Ensure unique, sorted, valid ports
            return sorted(list(set([p for p in ports if 1 <= p <= 65535])))
        
        # Fallback to Top 100
        return TOP_100_PORTS

    def execute_scan(self, scan_id: str, subnet: str, port_range_type: str, custom_ports: str = None, discovery_method: str = "ICMP", threads: int = 100):
        """
        Synchronously executes the scanning process.
        """
        start_time = time.time()
        self.db.create_scan(scan_id, target=subnet, scan_type=f"{discovery_method} Scan ({port_range_type})", status="RUNNING")
        
        ACTIVE_SCANS[scan_id] = {
            "status": "RUNNING",
            "progress": 0,
            "current_ip": "Initializing...",
            "target_port": "None",
            "elapsed": "00:00:00",
            "remaining": "~ 00:00:00"
        }

        try:
            self.db.insert_log("INFO", "ScanEngine", f"Starting host discovery phase on subnet: {subnet}")
            ACTIVE_SCANS[scan_id]["current_ip"] = "Discovering hosts..."
            
            # 1. Host Discovery Phase
            discoverer = HostDiscovery(max_threads=threads)
            hosts = discoverer.discover(subnet, method=discovery_method)
            
            self.db.insert_log("INFO", "ScanEngine", f"Host discovery completed. Found {len(hosts)} active hosts.")
            
            # Map selected ports
            ports_to_scan = self.get_ports_by_range_type(port_range_type, custom_ports)
            
            results = []
            total_hosts = len(hosts)

            # 2. Port Scanning Phase (Loop over active hosts)
            scanner = PortScanner(max_threads=threads)
            
            for idx, host in enumerate(hosts):
                ip = host["ip"]
                self.db.insert_log("INFO", "ScanEngine", f"Scanning host {ip} ({idx+1}/{total_hosts})...")
                
                ACTIVE_SCANS[scan_id]["current_ip"] = ip
                ACTIVE_SCANS[scan_id]["progress"] = int(((idx) / total_hosts) * 100)
                
                # Elapsed time formatting
                elapsed_seconds = int(time.time() - start_time)
                ACTIVE_SCANS[scan_id]["elapsed"] = self._format_seconds(elapsed_seconds)
                
                # Simple estimated remaining time
                if idx > 0:
                    time_per_host = elapsed_seconds / idx
                    remaining_hosts = total_hosts - idx
                    remaining_seconds = int(time_per_host * remaining_hosts)
                    ACTIVE_SCANS[scan_id]["remaining"] = f"~ {self._format_seconds(remaining_seconds)}"
                else:
                    ACTIVE_SCANS[scan_id]["remaining"] = "~ Calculating..."

                # Scan ports
                def update_port_progress(scanned, total):
                    if ports_to_scan:
                        p = ports_to_scan[min(scanned - 1, total - 1)]
                        ACTIVE_SCANS[scan_id]["target_port"] = str(p)
                
                open_ports = scanner.scan_host(ip, ports_to_scan, progress_callback=update_port_progress)
                
                # Attach the scanned ports list to host object
                host["ports"] = open_ports
                results.append(host)

            # Finalize progress
            duration = time.time() - start_time
            ACTIVE_SCANS[scan_id]["progress"] = 100
            ACTIVE_SCANS[scan_id]["status"] = "COMPLETED"
            ACTIVE_SCANS[scan_id]["elapsed"] = self._format_seconds(int(duration))
            ACTIVE_SCANS[scan_id]["remaining"] = "00:00:00"
            ACTIVE_SCANS[scan_id]["current_ip"] = "Finished"
            ACTIVE_SCANS[scan_id]["target_port"] = "None"

            # 3. Store Results in Database
            self.db.save_scan_results(scan_id, results, duration)
            
            # 4. Generate Reports
            # Fetch scan metadata and hosts from DB to guarantee schema parity
            scan_metadata = self.db.get_scan(scan_id)
            saved_hosts = self.db.get_scan_hosts(scan_id)
            
            ReportGenerator.generate_json(scan_id, scan_metadata, saved_hosts)
            ReportGenerator.generate_txt(scan_id, scan_metadata, saved_hosts)
            ReportGenerator.generate_csv(scan_id, scan_metadata, saved_hosts)
            
            self.db.insert_log("INFO", "ScanEngine", f"Scan {scan_id} reports generated successfully.")

        except Exception as e:
            logger.error(f"Error executing scan {scan_id}: {str(e)}")
            self.db.update_scan_status(scan_id, "FAILED")
            self.db.insert_log("ERROR", "ScanEngine", f"Scan {scan_id} failed: {str(e)}")
            ACTIVE_SCANS[scan_id]["status"] = "FAILED"
            ACTIVE_SCANS[scan_id]["current_ip"] = "Error"
            ACTIVE_SCANS[scan_id]["target_port"] = "Error"

    def launch_scan_async(self, subnet: str, port_range_type: str, custom_ports: str = None, discovery_method: str = "ICMP", threads: int = 100) -> str:
        """
        Launches a scan in a separate background thread.
        Returns the scan ID.
        """
        scan_id = f"SCAN-{uuid.uuid4().hex[:6].upper()}"
        
        t = threading.Thread(
            target=self.execute_scan,
            args=(scan_id, subnet, port_range_type, custom_ports, discovery_method, threads),
            daemon=True
        )
        t.start()
        return scan_id

    @staticmethod
    def _format_seconds(seconds: int) -> str:
        """
        Utility method to format duration into HH:MM:SS format.
        """
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
