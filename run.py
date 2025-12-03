#!/usr/bin/env python3
"""
PoS System Entry Point
Configures and runs the Flask application with optimized settings for performance.
"""
from app import app
import os

if __name__ == '__main__':
    # Get debug mode from environment variable (default to False for production)
    # Set FLASK_DEBUG=1 or FLASK_DEBUG=True to enable debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    
    # Bind to 0.0.0.0 to allow access from local network devices (Pixel phones, PCs)
    # Enable threading for concurrent request handling (Waiter + Kitchen simultaneous operations)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,  # Configurable debug mode (IMPORTANT: Disable in production)
        threaded=True  # Explicitly enable threading for concurrent requests
    )
