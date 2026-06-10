import os

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, "netdiscover.db")

# Report storage directory
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Default scanner settings
DEFAULT_TIMEOUT = 1.0  # seconds
DEFAULT_THREADS = 100
DEFAULT_BANNER_TIMEOUT = 2.0  # seconds

# Port categories
COMMON_PORTS = [
    21,   # FTP
    22,   # SSH
    23,   # Telnet
    25,   # SMTP
    53,   # DNS (TCP)
    80,   # HTTP
    110,  # POP3
    139,  # NetBIOS
    143,  # IMAP
    443,  # HTTPS
    445,  # SMB
    1433, # MS SQL
    1521, # Oracle
    3306, # MySQL
    3389, # RDP
    5432, # PostgreSQL
    5900, # VNC
    8080, # HTTP Proxy / Alternate
    8443, # HTTPS Alternate
]

# Top 100 most common ports (source: Nmap)
TOP_100_PORTS = sorted(list(set(COMMON_PORTS + [
    7, 9, 13, 17, 19, 26, 37, 79, 88, 111, 113, 119, 135, 144, 161, 179, 199, 389, 
    427, 465, 513, 514, 515, 543, 544, 548, 554, 563, 587, 631, 636, 990, 993, 
    995, 1025, 1026, 1027, 1028, 1029, 1110, 1434, 1720, 1723, 2000, 2049, 2121, 
    2301, 3128, 3268, 3269, 5000, 5060, 5631, 5800, 5984, 6000, 6001, 6646, 6667, 
    7000, 8000, 8008, 8081, 8888, 9000, 9001, 9090, 9100, 9999, 32768, 49152, 49153, 
    49154, 49155, 49156, 49157
])))

# For Top 1000, we can define a broader list or range, or select a list of well-known ports.
# We will construct a list of Top 1000 ports by merging Top 100 and other standard service ports.
TOP_1000_PORTS = sorted(list(set(TOP_100_PORTS + [
    # Add more ports to make a robust set of common TCP ports
    53, 67, 68, 69, 80, 81, 82, 83, 84, 85, 88, 102, 104, 109, 110, 111, 113, 115, 119, 123, 135, 137, 138, 139,
    143, 161, 162, 179, 389, 443, 444, 445, 464, 465, 500, 513, 514, 515, 520, 543, 544, 546, 547, 548, 554, 563,
    587, 631, 636, 646, 873, 902, 989, 990, 993, 995, 1080, 1194, 1234, 1433, 1434, 1521, 1604, 1723, 1883, 1900,
    2049, 2082, 2083, 2086, 2087, 2095, 2096, 2100, 2181, 2222, 2375, 2376, 2483, 2484, 2947, 3000, 3050, 3260,
    3306, 3307, 3389, 3535, 3689, 3690, 4000, 4111, 4125, 4242, 4500, 4840, 5000, 5001, 5050, 5060, 5061, 5190,
    5222, 5223, 5269, 5280, 5353, 5357, 5432, 5555, 5631, 5671, 5672, 5800, 5900, 5901, 5902, 5938, 5984, 5985,
    5986, 6000, 6001, 6002, 6379, 6443, 6543, 6667, 7000, 7001, 7002, 7077, 7080, 7443, 7777, 8000, 8008, 8080,
    8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088, 8089, 8181, 8200, 8443, 8500, 8883, 8888, 9000, 9001, 9042,
    9092, 9100, 9200, 9300, 9418, 9443, 9999, 10000, 11211, 27017, 27018, 27019, 28017, 32400, 50000
])))
