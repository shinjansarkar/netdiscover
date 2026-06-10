# Use official lightweight Python image
FROM python:3.10-slim

# Install system dependencies needed for network commands and scapy
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    net-tools \
    tcpdump \
    libpcap-dev \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY netdiscover/ ./netdiscover/
COPY run.py .

# Expose port for dashboard
EXPOSE 5000

# Run Flask server
CMD ["python", "run.py"]
