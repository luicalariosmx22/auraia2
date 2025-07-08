# gunicorn_config.py
# Configuration for Gunicorn WSGI server

import os
from gevent import monkey
monkey.patch_all()

# Basic configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
worker_class = "gevent"
workers = 1
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Application
wsgi_app = "app:app"
