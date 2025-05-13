# clientes/aura/extensiones.py ✅

from flask_socketio import SocketIO
from flask_session import Session  # AÑADIR
from apscheduler.schedulers.background import BackgroundScheduler  # AÑADIR
import pytz  # AÑADIR

socketio = SocketIO()
session_ext = Session()  # AÑADIR
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Hermosillo'))  # AÑADIR
