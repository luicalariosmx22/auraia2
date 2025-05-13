# clientes/aura/extensions.py
from flask_socketio import SocketIO
from flask_session import Session
from flask_session.sessions import SessionInterface
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

class CustomSessionInterface(SessionInterface):
    def open_session(self, app, request):
        # Sobrescribe el acceso a session_cookie_name
        sid = request.cookies.get(app.config.get('SESSION_COOKIE_NAME', 'session'))
        if not sid:
            return None
        return self.session_class(sid)

    def save_session(self, app, session, response):
        # Implementa el guardado de la sesión si es necesario
        pass

socketio = SocketIO()
session_ext = Session()
session_ext.session_interface = CustomSessionInterface()  # Usa la clase personalizada
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Hermosillo'))