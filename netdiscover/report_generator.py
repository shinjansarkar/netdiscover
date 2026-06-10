import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from netdiscover.config import REPORTS_DIR

class ReportGenerator:
    """
    Handles report generation for network scans in TXT, JSON, and CSV formats.
    """

    @staticmethod
    def generate_json(scan_id: str, scan_metadata: Dict[str, Any], hosts: List[Dict[str, Any]]) -> str:
        """
        Generates a JSON report and saves it to the reports folder.
        Returns the absolute filepath.
        """
        filename = f"report_{scan_id}.json"
        filepath = os.path.join(REPORTS_DIR, filename)

        report_data = {
            "report_id": scan_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "target": scan_metadata.get("target"),
                "scan_type": scan_metadata.get("scan_type"),
                "status": scan_metadata.get("status"),
                "duration_seconds": scan_metadata.get("duration", 0),
                "hosts_found": len(hosts)
            },
            "hosts": []
        }

        for host in hosts:
            host_entry = {
                "ip": host["ip_address"],
                "hostname": host["hostname"],
                "status": host["status"],
                "mac": host.get("mac_address", "Unknown"),
                "response_time": host.get("response_time", "0ms"),
                "os": host.get("os_detected", "Unknown"),
                "open_ports": []
            }
            for port in host.get("ports", []):
                host_entry["open_ports"].append({
                    "port": port["port"],
                    "service": port["service"],
                    "product": port.get("product", "Unknown"),
                    "version": port.get("version", "Unknown"),
                    "banner": port.get("banner")
                })
            report_data["hosts"].append(host_entry)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4)

        return filepath

    @staticmethod
    def generate_txt(scan_id: str, scan_metadata: Dict[str, Any], hosts: List[Dict[str, Any]]) -> str:
        """
        Generates a readable TXT report and saves it.
        Returns the absolute filepath.
        """
        filename = f"report_{scan_id}.txt"
        filepath = os.path.join(REPORTS_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f" NETDISCOVER SECURITY AUDIT REPORT - {scan_id}\n")
            f.write(f" Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            f.write("SCAN METADATA:\n")
            f.write(f"  Target Subnet: {scan_metadata.get('target')}\n")
            f.write(f"  Scan Type:     {scan_metadata.get('scan_type')}\n")
            f.write(f"  Status:        {scan_metadata.get('status')}\n")
            f.write(f"  Duration:      {scan_metadata.get('duration', 0):.2f} seconds\n")
            f.write(f"  Hosts Found:   {len(hosts)}\n\n")

            f.write("DISCOVERED HOSTS & SERVICES:\n")
            f.write("-" * 80 + "\n")

            for host in hosts:
                f.write(f"Host: {host['ip_address']} ({host['hostname']})\n")
                f.write(f"  Status:        {host['status']}\n")
                f.write(f"  MAC Address:   {host.get('mac_address', 'Unknown')}\n")
                f.write(f"  Latency:       {host.get('response_time', '0ms')}\n")
                f.write(f"  Likely OS:     {host.get('os_detected', 'Unknown')}\n")
                
                ports = host.get("ports", [])
                if ports:
                    f.write("  Open Ports:\n")
                    f.write("    PORT      STATE    SERVICE      PRODUCT / VERSION / BANNER\n")
                    f.write("    ----      -----    -------      --------------------------\n")
                    for port in ports:
                        prod_ver = f"{port.get('product', 'Unknown')} {port.get('version', 'Unknown')}"
                        if port.get('banner'):
                            prod_ver += f" (Banner: {port['banner']})"
                        f.write(f"    {str(port['port']).ljust(9)} {port['state'].ljust(8)} {port['service'].ljust(12)} {prod_ver}\n")
                else:
                    f.write("  Open Ports: None detected (or scanned)\n")
                
                f.write("-" * 80 + "\n")

        return filepath

    @staticmethod
    def generate_csv(scan_id: str, scan_metadata: Dict[str, Any], hosts: List[Dict[str, Any]]) -> str:
        """
        Generates a flat CSV spreadsheet of open ports.
        Returns the absolute filepath.
        """
        filename = f"report_{scan_id}.csv"
        filepath = os.path.join(REPORTS_DIR, filename)

        fields = [
            "ScanID", "TargetSubnet", "IPAddress", "Hostname", "HostStatus", 
            "MACAddress", "ResponseTime", "OSDetected", "Port", "Protocol", 
            "Service", "PortState", "Product", "Version", "Banner"
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

            for host in hosts:
                ports = host.get("ports", [])
                if not ports:
                    # Write host row with empty port info
                    writer.writerow([
                        scan_id, scan_metadata.get("target"), host["ip_address"], host["hostname"], 
                        host["status"], host.get("mac_address", "Unknown"), host.get("response_time", "0ms"), 
                        host.get("os_detected", "Unknown"), "", "", "", "", "", "", ""
                    ])
                else:
                    for port in ports:
                        writer.writerow([
                            scan_id, scan_metadata.get("target"), host["ip_address"], host["hostname"], 
                            host["status"], host.get("mac_address", "Unknown"), host.get("response_time", "0ms"), 
                            host.get("os_detected", "Unknown"), port["port"], "tcp", 
                            port["service"], port["state"], port.get("product", "Unknown"), 
                            port.get("version", "Unknown"), port.get("banner", "")
                        ])

        return filepath
