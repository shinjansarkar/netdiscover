import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
from netdiscover.db import Database
from netdiscover.scanner_engine import ScannerEngine, ACTIVE_SCANS
from netdiscover.config import REPORTS_DIR
from netdiscover.init_helper import populate_initial_data_if_empty

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Core instances
db = Database()
engine = ScannerEngine(db)

# Pre-populate database if empty (ensuring reference mock data displays on first boot)
populate_initial_data_if_empty(db)

@app.route('/')
def dashboard():
    """
    Renders the main dashboard index page.
    """
    stats = db.get_dashboard_stats()
    scans = db.get_all_scans()
    
    latest_scan = scans[0] if scans else None
    hosts = []
    if latest_scan:
        hosts = db.get_scan_hosts(latest_scan["id"])
        
    return render_template(
        'index.html',
        stats=stats,
        scans=scans,
        latest_scan=latest_scan,
        hosts=hosts,
        active_tab='dashboard'
    )

@app.route('/new_scan_page')
def new_scan_page():
    """
    Renders the page to configure and trigger a scan.
    """
    scans = db.get_all_scans()
    return render_template(
        'new_scan.html',
        scans=scans,
        active_tab='new_scan'
    )

@app.route('/scan_history_page')
def scan_history_page():
    """
    Renders the scan history table.
    """
    scans = db.get_all_scans()
    selected_scan_id = request.args.get('scan_id')
    
    selected_scan = None
    hosts = []
    
    if selected_scan_id:
        selected_scan = db.get_scan(selected_scan_id)
        if selected_scan:
            hosts = db.get_scan_hosts(selected_scan_id)
    elif scans:
        selected_scan = scans[0]
        hosts = db.get_scan_hosts(selected_scan["id"])

    return render_template(
        'scan_history.html',
        scans=scans,
        selected_scan=selected_scan,
        hosts=hosts,
        active_tab='scan_history'
    )

@app.route('/reports_page')
def reports_page():
    """
    Renders the report viewing and download interface.
    """
    scans = db.get_all_scans()
    selected_scan_id = request.args.get('scan_id')
    
    selected_scan = None
    hosts = []
    json_report_content = None
    
    if selected_scan_id:
        selected_scan = db.get_scan(selected_scan_id)
    elif scans:
        selected_scan = scans[0]
        
    if selected_scan:
        hosts = db.get_scan_hosts(selected_scan["id"])
        # Attempt to load the JSON report content if available
        json_path = os.path.join(REPORTS_DIR, f"report_{selected_scan['id']}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_report_content = json.dumps(json.load(f), indent=4)
            except Exception:
                json_report_content = "// Error loading report file"

    return render_template(
        'reports.html',
        scans=scans,
        selected_scan=selected_scan,
        hosts=hosts,
        json_report_content=json_report_content,
        active_tab='reports'
    )

@app.route('/logs_page')
def logs_page():
    """
    Renders the live and historical system logs page.
    """
    scans = db.get_all_scans()
    logs = db.get_logs(limit=100)
    return render_template(
        'logs.html',
        scans=scans,
        logs=logs,
        active_tab='logs'
    )

# --- API Endpoints ---

@app.route('/api/scan/launch', methods=['POST'])
def api_launch_scan():
    """
    Launches a subnet scan in the background.
    """
    data = request.json or {}
    subnet = data.get('subnet', '192.168.1.0/24')
    port_range = data.get('port_range', 'top100')
    custom_ports = data.get('custom_ports', '')
    discovery_method = data.get('discovery_method', 'ICMP')
    threads = int(data.get('threads', 100))

    try:
        # Launch scan async
        scan_id = engine.launch_scan_async(
            subnet=subnet,
            port_range_type=port_range,
            custom_ports=custom_ports,
            discovery_method=discovery_method,
            threads=threads
        )
        return jsonify({
            "status": "success",
            "scan_id": scan_id,
            "message": f"Scan started successfully with ID {scan_id}."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/api/scan/status/<scan_id>')
def api_scan_status(scan_id):
    """
    Returns live progress status of an active scan.
    """
    status_data = ACTIVE_SCANS.get(scan_id)
    if not status_data:
        # Check if completed and stored in DB
        scan = db.get_scan(scan_id)
        if scan:
            return jsonify({
                "status": scan["status"],
                "progress": 100 if scan["status"] == "COMPLETED" else 0,
                "current_ip": "Finished",
                "target_port": "None",
                "elapsed": f"{int(scan['duration'])}s",
                "remaining": "00:00:00"
            })
        return jsonify({"status": "NOT_FOUND"}), 404
        
    return jsonify(status_data)

@app.route('/api/logs')
def api_get_logs():
    """
    Endpoint to retrieve system logs in JSON format.
    """
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level', None)
    logs = db.get_logs(limit=limit, level=level)
    return jsonify(logs)

@app.route('/reports/download/<scan_id>/<file_format>')
def download_report(scan_id, file_format):
    """
    Handles report downloads for TXT, JSON, and CSV.
    """
    file_format = file_format.lower()
    if file_format not in ['json', 'txt', 'csv']:
        return "Invalid format", 400
        
    filename = f"report_{scan_id}.{file_format}"
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # Flask app start listener
    # Ensure folders exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
