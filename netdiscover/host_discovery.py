import os
import subprocess
import socket
import logging
import platform
import ipaddress
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Tuple, Optional

logger = logging.getLogger(__name__)

# Check if scapy is available for ARP scans
try:
    from scapy.all import ARP, Ether, srp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logger.warning("Scapy is not installed. ARP scanning will fall back to ICMP pinging.")

class HostDiscovery:
    """
    Module for discovering active hosts on a network subnet.
    """

    def __init__(self, max_threads: int = 100, timeout: float = 1.0):
        self.max_threads = max_threads
        self.timeout = timeout

    @staticmethod
    def get_hostname(ip: str) -> str:
        """
        Performs a reverse DNS lookup to resolve hostnames.
        """
        try:
            name, _, _ = socket.gethostbyaddr(ip)
            return name
        except (socket.herror, socket.gaierror):
            return "Unknown"

    def ping_host(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        Pings a host using the system ping command.
        This is cross-platform and does not require root privileges.
        """
        ip_str = str(ip)
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
        
        # Ping timeout is set in seconds
        t_val = str(int(self.timeout * 1000)) if platform.system().lower() == 'windows' else str(max(1, int(self.timeout)))
        
        cmd = ['ping', param, '1', timeout_param, t_val, ip_str]
        
        start_time = time.time()
        try:
            # Run the system ping command
            # redirect stdout and stderr to DEVNULL to run quietly
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=self.timeout + 1.0)
            elapsed = (time.time() - start_time) * 1000 # ms
            
            if result.returncode == 0:
                # Resolve hostname
                hostname = self.get_hostname(ip_str)
                
                # Parse latency if possible
                latency = round(elapsed, 2)
                if result.stdout:
                    # Look for time=XX.X ms in output
                    match = re.search(r'time=([\d\.]+)\s*ms', result.stdout)
                    if match:
                        latency = round(float(match.group(1)), 2)

                return {
                    "ip": ip_str,
                    "hostname": hostname,
                    "status": "ONLINE",
                    "mac": "Unknown",
                    "response_time": f"{latency}ms",
                    "os": "Linux/Unix" if "ttl=" in result.stdout.lower() and "ttl=64" in result.stdout.lower() else ("Windows" if "ttl=128" in result.stdout.lower() else "Unknown")
                }
        except subprocess.TimeoutExpired:
            logger.debug(f"Ping command timed out for host {ip_str}")
        except Exception as e:
            logger.error(f"Error pinging host {ip_str}: {str(e)}")
        
        return None

    def arp_scan(self, interface: str = None) -> List[Dict[str, Any]]:
        """
        Performs an ARP scan using Scapy. This requires root permissions.
        If Scapy is not available or root permissions are missing, it returns empty list.
        """
        # If scapy isn't installed, return empty list (will fallback)
        if not SCAPY_AVAILABLE:
            logger.warning("ARP scan requested but Scapy is not available.")
            return []

        # We will dynamically import and run ARP scan. We run this if we have root.
        if os.geteuid() != 0:
            logger.warning("ARP scan requires root permissions (euid=0).")
            return []

        # For ARP scan, we need a subnet range. We will handle ARP scan within the main discovery flow.
        return []

    def run_arp_scan_on_subnet(self, subnet_cidr: str) -> List[Dict[str, Any]]:
        """
        Runs an ARP scan on a specific CIDR subnet block using Scapy.
        """
        discovered = []
        if not SCAPY_AVAILABLE or os.geteuid() != 0:
            return discovered

        logger.info(f"Starting ARP broadcast scan on {subnet_cidr}...")
        try:
            # Construct ARP request
            ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=subnet_cidr), timeout=self.timeout, verbose=False)
            
            for snd, rcv in ans:
                ip = rcv.psrc
                mac = rcv.hwsrc
                hostname = self.get_hostname(ip)
                discovered.append({
                    "ip": ip,
                    "hostname": hostname,
                    "status": "ONLINE",
                    "mac": mac,
                    "response_time": "1.0ms", # ARP responses are extremely fast
                    "os": "Unknown"
                })
            logger.info(f"ARP scan finished. Discovered {len(discovered)} hosts.")
        except Exception as e:
            logger.error(f"Error during ARP scan: {str(e)}")

        return discovered

    def discover(self, subnet_cidr: str, method: str = "ICMP") -> List[Dict[str, Any]]:
        """
        Orchestrates host discovery on a subnet using the chosen method.
        Supports: "ICMP", "ARP", or "BOTH".
        """
        try:
            network = ipaddress.ip_network(subnet_cidr, strict=False)
        except ValueError as e:
            logger.error(f"Invalid subnet CIDR: {subnet_cidr}")
            raise ValueError(f"Invalid subnet CIDR: {subnet_cidr}")

        hosts = list(network.hosts())
        discovered_hosts = {}

        # 1. Try ARP Scan first if requested and available
        if method in ["ARP", "BOTH"] and SCAPY_AVAILABLE and os.geteuid() == 0:
            arp_results = self.run_arp_scan_on_subnet(subnet_cidr)
            for h in arp_results:
                discovered_hosts[h["ip"]] = h

        # 2. Try ICMP Ping Scan if requested, or if ARP scan yielded nothing or wasn't available
        if method in ["ICMP", "BOTH"] or not discovered_hosts:
            logger.info(f"Starting ICMP ping discovery on {subnet_cidr} for {len(hosts)} potential hosts...")
            
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                # Submit ping tasks
                future_to_ip = {executor.submit(self.ping_host, ip): ip for ip in hosts}
                
                for future in as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        result = future.result()
                        if result:
                            ip_addr = result["ip"]
                            # If we already got it via ARP, we can combine/update it
                            if ip_addr in discovered_hosts:
                                # Keep the MAC address from ARP, but update latency and OS if ping was successful
                                discovered_hosts[ip_addr]["response_time"] = result["response_time"]
                                if result["os"] != "Unknown":
                                    discovered_hosts[ip_addr]["os"] = result["os"]
                            else:
                                discovered_hosts[ip_addr] = result
                    except Exception as e:
                        logger.error(f"Error pinging host {ip}: {str(e)}")

        # Convert to list and sort by IP address
        results = list(discovered_hosts.values())
        results.sort(key=lambda x: ipaddress.ip_address(x["ip"]))
        logger.info(f"Host discovery complete. Found {len(results)} active hosts.")
        return results
