# clientes/aura/extensions/socketio_instance.py
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")
