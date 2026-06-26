import socket
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
from netdiscover.config import DEFAULT_TIMEOUT, DEFAULT_THREADS
from netdiscover.banner_grabber import BannerGrabber
from netdiscover.service_detector import ServiceDetector

logger = logging.getLogger(__name__)

class PortScanner:
    """
    Multithreaded TCP Port Scanner.
    """

    def __init__(self, timeout: float = DEFAULT_TIMEOUT, max_threads: int = DEFAULT_THREADS):
        self.timeout = timeout
        self.max_threads = max_threads

    def scan_single_port(self, ip: str, port: int) -> Dict[str, Any]:
        """
        Scans a single TCP port on a given IP address.
        Returns detailed results if the port is open, otherwise returns None.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((ip, port))
                if result == 0:
                    # Port is open! Grab banner and detect service.
                    banner = BannerGrabber.grab(ip, port)
                    service_info = ServiceDetector.detect(port, banner)
                    
                    return {
                        "port": port,
                        "state": "OPEN",
                        "service": service_info["name"],
                        "product": service_info["product"],
                        "version": service_info["version"],
                        "banner": banner
                    }
        except (socket.timeout, OSError) as e:
            logger.debug(f"Socket error scanning {ip}:{port} - {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error scanning port {port} on {ip}: {str(e)}")
        
        return {
            "port": port,
            "state": "CLOSED",
            "service": "Unknown",
            "product": "Unknown",
            "version": "Unknown",
            "banner": None
        }

    def scan_host(self, ip: str, ports: List[int], progress_callback: Callable[[int, int], None] = None) -> List[Dict[str, Any]]:
        """
        Scans a list of TCP ports on a target IP address using a ThreadPoolExecutor.
        """
        open_ports = []
        total_ports = len(ports)
        scanned_count = 0

        logger.info(f"Starting port scan on {ip} for {total_ports} ports...")

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all port scan tasks
            future_to_port = {executor.submit(self.scan_single_port, ip, port): port for port in ports}
            
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    scanned_count += 1
                    
                    if progress_callback:
                        progress_callback(scanned_count, total_ports)

                    if result and result["state"] == "OPEN":
                        open_ports.append(result)
                        logger.debug(f"Port {port} is OPEN on {ip}: {result['service']} ({result['product']} {result['version']})")
                except Exception as e:
                    logger.error(f"Error reading scan result for port {port} on {ip}: {str(e)}")

        # Sort the open ports list for clean reporting
        open_ports.sort(key=lambda x: x["port"])
        logger.info(f"Completed port scan on {ip}. Found {len(open_ports)} open ports.")
        return open_ports
