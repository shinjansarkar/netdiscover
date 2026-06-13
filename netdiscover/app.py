import os
import json
import logging
import ipaddress
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

# Keep startup clean; do not auto-populate demo/history data.
# populate_initial_data_if_empty(db)


def _parse_patterns_from_env(var_name: str) -> list:
    raw = os.getenv(var_name, "")
    if not raw:
        return []
    return [p.strip() for p in raw.split(',') if p.strip()]


def _target_matches_pattern(target: str, pattern: str) -> bool:
    """
    Match target (IP or CIDR) against an IP/CIDR pattern.
    """
    try:
        t = str(target).strip()
        p = str(pattern).strip()

        t_net = ipaddress.ip_network(t, strict=False) if '/' in t else ipaddress.ip_network(f"{t}/32", strict=False)
        p_net = ipaddress.ip_network(p, strict=False) if '/' in p else ipaddress.ip_network(f"{p}/32", strict=False)

        return t_net.subnet_of(p_net) or p_net.subnet_of(t_net) or t_net.overlaps(p_net)
    except Exception:
        return False


def _is_private_target(target: str) -> bool:
    """
    Returns True if target (IP or CIDR) is private.
    """
    try:
        t = str(target).strip()
        if '/' in t:
            net = ipaddress.ip_network(t, strict=False)
            return net.is_private
        ip = ipaddress.ip_address(t)
        return ip.is_private
    except Exception:
        return False


def _get_visible_scans() -> list:
    """
    Returns scans visible in UI history dropdowns.
    Policy:
    - hide targets matching HISTORY_EXCLUDE_TARGETS env list (comma separated IP/CIDR)
    """
    scans = db.get_all_scans()
    hidden_patterns = _parse_patterns_from_env('HISTORY_EXCLUDE_TARGETS')

    visible = []
    for s in scans:
        target = s.get('target', '')
        hidden = any(_target_matches_pattern(target, p) for p in hidden_patterns)
        if hidden:
            continue

        visible.append(s)

    return visible

@app.route('/')
def dashboard():
    """
    Renders the main dashboard index page.
    """
    stats = db.get_dashboard_stats()
    scans = _get_visible_scans()
    
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
    scans = _get_visible_scans()
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
    all_scans = _get_visible_scans()
    selected_scan_id = request.args.get('scan_id')
    
    selected_scan = None
    hosts = []
    
    if selected_scan_id:
        selected_scan = db.get_scan(selected_scan_id)
        if selected_scan:
            hosts = db.get_scan_hosts(selected_scan_id)
    elif all_scans:
        selected_scan = all_scans[0]
        hosts = db.get_scan_hosts(selected_scan["id"])

    # Keep dropdown minimal: only show the currently selected/loaded scan.
    scans = [selected_scan] if selected_scan else []

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
    all_scans = _get_visible_scans()
    selected_scan_id = request.args.get('scan_id')
    
    selected_scan = None
    hosts = []
    json_report_content = None
    
    if selected_scan_id:
        selected_scan = db.get_scan(selected_scan_id)
    elif all_scans:
        selected_scan = all_scans[0]
        
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

    # Keep dropdown minimal here as well.
    scans = [selected_scan] if selected_scan else []

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
    scans = _get_visible_scans()
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

    # Default behavior: keep scan history in DB unless explicitly disabled.
    record_results = bool(request.json.get('record_results', True)) if request.json else True

    # Optional hard hide from history/reports
    hide_from_history = bool(request.json.get('hide_from_history', False)) if request.json else False
    if hide_from_history:
        record_results = False

    # Optional router metadata (for topology accuracy / immediate UI mapping)
    router_info = None
    if request.json:
        rmac = request.json.get('router_mac')
        rport = request.json.get('router_port')
        rip = request.json.get('router_ip')
        if any([rmac, rport, rip]):
            router_info = {
                'mac': rmac,
                'port': rport,
                'ip': rip,
                'hostname': request.json.get('router_hostname', 'router')
            }
    # Optional exclude list: array of IPs or CIDR strings to omit from history/reports
    exclude_list = None
    if request.json:
        exclude_list = request.json.get('exclude')
        if exclude_list and not isinstance(exclude_list, list):
            exclude_list = None

    try:
        # Launch scan async
        scan_id = engine.launch_scan_async(
            subnet=subnet,
            port_range_type=port_range,
            custom_ports=custom_ports,
            discovery_method=discovery_method,
            threads=threads,
            record_results=record_results,
            router_info=router_info,
            exclude_list=exclude_list
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
