"""
Gunicorn configuration for Zeabur deployment
"""
import os
import multiprocessing

# Bind to PORT from environment (Zeabur sets this)
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"

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
