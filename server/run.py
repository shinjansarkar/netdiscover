#!/usr/bin/env python3
import os
import sys

# Ensure the root path is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from netdiscover.app import app

if __name__ == '__main__':
    # Initialize port
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Starting NetDiscover Dashboard on http://0.0.0.0:{port}")
    
    # Set debug=False for production security
    app.run(host='0.0.0.0', port=port, debug=False)
