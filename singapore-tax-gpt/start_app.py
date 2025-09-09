#!/usr/bin/env python
"""Simple wrapper to start Streamlit with Railway's PORT."""

import os
import sys
import streamlit.web.cli as stcli

if __name__ == '__main__':
    # Get PORT from environment or default to 8080
    port = os.environ.get('PORT', '8080')
    
    # Build Streamlit args
    sys.argv = [
        'streamlit',
        'run',
        'app_main.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ]
    
    # Start Streamlit
    sys.exit(stcli.main())