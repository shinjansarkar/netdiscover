import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ServiceDetector:
    """
    Class to detect services and version info running on specific ports
    based on port numbers and banners.
    """

    # Common port maps to standard service names
    PORT_MAP = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        111: "RPCBind",
        135: "MSRPC",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        993: "IMAPS",
        995: "POP3S",
        1433: "MS-SQL",
        1521: "Oracle",
        2049: "NFS",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        6379: "Redis",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt",
        9200: "Elasticsearch",
        27017: "MongoDB"
    }

    @classmethod
    def detect(cls, port: int, banner: str = None) -> Dict[str, Any]:
        """
        Detects the service name and version based on port and banner.
        Returns a dict with 'name', 'version', and 'product' keys.
        """
        service_name = cls.PORT_MAP.get(port, "Unknown")
        product = "Unknown"
        version = "Unknown"

        if not banner:
            return {
                "name": service_name,
                "product": product,
                "version": version
            }

        # Clean the banner line for parsing
        clean_banner = banner.replace('\r', '').replace('\n', ' ').strip()

        # SSH banner regex
        # Example: SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5
        ssh_match = re.search(r'SSH-([\d\.]+)-([^\s_]+)_([^\s]+)(?:\s+(.*))?', clean_banner, re.IGNORECASE)
        if ssh_match:
            service_name = "SSH"
            product = ssh_match.group(2)  # OpenSSH, Dropbear, etc.
            version = ssh_match.group(3)
            if ssh_match.group(4):
                version += f" ({ssh_match.group(4)})"
            return {"name": service_name, "product": product, "version": version}

        # HTTP banner parsing (from Server header or basic response)
        # Example: Server: Apache/2.4.41 (Ubuntu)
        server_match = re.search(r'Server:\s*([^\r\n/]+)/?([^\s\r\n]*)', clean_banner, re.IGNORECASE)
        if server_match:
            product = server_match.group(1).strip()
            version = server_match.group(2).strip()
            if not version:
                version = "Unknown"
            if "apache" in product.lower():
                service_name = "HTTP"
            elif "nginx" in product.lower():
                service_name = "HTTP"
            elif "microsoft-iis" in product.lower():
                service_name = "HTTP"
            return {"name": service_name, "product": product, "version": version}

        # HTTP responses without a "Server:" prefix but starting with HTTP/1.x
        if clean_banner.startswith("HTTP/"):
            # Check if there is any Server header embedded anywhere in the multiline response
            server_in_body = re.search(r'server:\s*([^\s/]+)/?([^\s]*)', clean_banner, re.IGNORECASE)
            if server_in_body:
                product = server_in_body.group(1).strip()
                version = server_in_body.group(2).strip() or "Unknown"
                return {"name": "HTTP", "product": product, "version": version}
            else:
                return {"name": "HTTP", "product": "Generic Web Server", "version": "Unknown"}

        # FTP banner parsing
        # Example: 220 (vsFTPd 3.0.3) or 220 ProFTPD 1.3.5 Server
        if clean_banner.startswith("220"):
            service_name = "FTP"
            if "vsftpd" in clean_banner.lower():
                product = "vsFTPd"
                ver_match = re.search(r'vsftpd\s+([\d\.]+)', clean_banner, re.IGNORECASE)
                if ver_match:
                    version = ver_match.group(1)
            elif "proftpd" in clean_banner.lower():
                product = "ProFTPD"
                ver_match = re.search(r'proftpd\s+([\d\.]+)', clean_banner, re.IGNORECASE)
                if ver_match:
                    version = ver_match.group(1)
            elif "pure-ftpd" in clean_banner.lower():
                product = "Pure-FTPd"
            else:
                product = "Generic FTP"
            return {"name": service_name, "product": product, "version": version}

        # SMTP banner parsing
        # Example: 220 mail.example.com ESMTP Postfix
        if clean_banner.startswith("220") and ("smtp" in clean_banner.lower() or "postfix" in clean_banner.lower() or "exim" in clean_banner.lower()):
            service_name = "SMTP"
            if "postfix" in clean_banner.lower():
                product = "Postfix"
            elif "exim" in clean_banner.lower():
                product = "Exim"
            elif "sendmail" in clean_banner.lower():
                product = "Sendmail"
            else:
                product = "Generic SMTP"
            return {"name": service_name, "product": product, "version": version}

        # Redis parsing
        # If the response contains Redis protocol error or output
        if "-ERR " in clean_banner or "+OK" in clean_banner:
            service_name = "Redis"
            product = "Redis Key-Value Store"
            return {"name": service_name, "product": product, "version": version}

        # MySQL parsing
        # MySQL protocol packet often has mysql_native_password or version info in raw bytes
        if "mysql" in clean_banner.lower() or "mariadb" in clean_banner.lower():
            service_name = "MySQL"
            product = "MariaDB" if "mariadb" in clean_banner.lower() else "MySQL"
            # Attempt to extract version like 5.7.29 or 10.4.11-MariaDB
            ver_match = re.search(r'([\d\.-]+-mariadb|[\d\.]+)', clean_banner, re.IGNORECASE)
            if ver_match:
                version = ver_match.group(1)
            return {"name": service_name, "product": product, "version": version}

        # If banner is set, we can store it as product info or try basic matching
        if len(clean_banner) > 0:
            product = clean_banner[:50]  # truncate long banners

        return {
            "name": service_name,
            "product": product,
            "version": version
        }
