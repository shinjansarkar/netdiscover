import socket
import logging
from typing import Optional
from netdiscover.config import DEFAULT_BANNER_TIMEOUT

logger = logging.getLogger(__name__)

class BannerGrabber:
    """
    Utility class to perform banner grabbing on open TCP ports.
    """

    @staticmethod
    def grab(ip: str, port: int, timeout: float = DEFAULT_BANNER_TIMEOUT) -> Optional[str]:
        """
        Attempts to grab a banner from a specified IP and port.
        It connects via socket and reads initial response, or sends a basic request if needed.
        """
        banner = None
        try:
            # We connect using TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                # Connect
                s.connect((ip, port))
                
                # Some protocols require us to send data first to get a banner,
                # while others (like SSH, FTP, SMTP) send a banner immediately.
                # Let's try reading immediately with a short timeout first.
                try:
                    data = s.recv(1024)
                    if data:
                        banner = data.decode('utf-8', errors='ignore').strip()
                        return banner
                except socket.timeout:
                    # No immediate response, which is normal for HTTP/HTTPS/etc.
                    pass

                # If no immediate banner was sent, let's send a generic probe if it's a common port
                if port in [80, 8080, 8000]:
                    # Send a simple HTTP GET request
                    s.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                    data = s.recv(1024)
                    if data:
                        banner = data.decode('utf-8', errors='ignore').strip()
                elif port == 443:
                    # For HTTPS, we can't easily negotiate SSL/TLS and grab plaintext here without ssl context.
                    # But we can try a basic SSL wrap or just return that it is likely SSL.
                    # We will return None and let service detector identify it.
                    pass
                else:
                    # Send a generic newline to trigger a response from interactive protocols
                    try:
                        s.sendall(b"\r\n")
                        data = s.recv(1024)
                        if data:
                            banner = data.decode('utf-8', errors='ignore').strip()
                    except Exception:
                        pass
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logger.debug(f"Banner grab failed on {ip}:{port} - {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error grabbing banner on {ip}:{port} - {str(e)}")

        return banner
