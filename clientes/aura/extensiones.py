# clientes/aura/extensions.py
from flask_socketio import SocketIO
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

socketio = SocketIO()
session_ext = Session()
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Hermosillo'))