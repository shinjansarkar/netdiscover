# Production-ready Python Flask backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies needed for potential scapy or raw socket operations
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpcap-dev iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for reports if it doesn't exist
RUN mkdir -p reports

# Expose port
EXPOSE 5000

# We use gunicorn for production instead of the Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
