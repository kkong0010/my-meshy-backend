"""
Gunicorn configuration for Zeabur deployment
"""
import os
import sys

# CRITICAL: Read PORT from environment - Zeabur sets this dynamically
port = os.environ.get('PORT', '8080')
print(f"[DEBUG] PORT environment variable: {port}", file=sys.stderr, flush=True)
print(f"[DEBUG] All env vars: {list(os.environ.keys())}", file=sys.stderr, flush=True)

# Bind to the port Zeabur assigned
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = 1  # Single worker to avoid memory issues
worker_class = 'sync'
worker_connections = 1000
timeout = 600  # 10 minutes for long-running 3D generation

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'

# Server mechanics
daemon = False
pidfile = None
preload_app = False

# Print configuration on startup
print(f"[GUNICORN CONFIG] Binding to: {bind}")
print(f"[GUNICORN CONFIG] Workers: {workers}")
print(f"[GUNICORN CONFIG] Timeout: {timeout}s")
