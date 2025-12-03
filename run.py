#!/usr/bin/env python3
"""
PoS System Entry Point
Configures and runs the Flask application with optimized settings for performance.
"""
from app import app

if __name__ == '__main__':
    # Bind to 0.0.0.0 to allow access from local network devices (Pixel phones, PCs)
    # Enable threading for concurrent request handling (Waiter + Kitchen simultaneous operations)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True  # Explicitly enable threading for concurrent requests
    )
