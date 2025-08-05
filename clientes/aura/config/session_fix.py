import logging
import os
from flask import Flask, session
from flask_session import FileSystemSessionInterface, Session

logger = logging.getLogger(__name__)

class CustomSessionInterface(FileSystemSessionInterface):
    def save_session(self, app, session, response):
        try:
            if hasattr(session, 'sid') and isinstance(session.sid, bytes):
                try:
                    session.sid = session.sid.decode('utf-8')
                except UnicodeDecodeError:
                    session.sid = session.sid.hex()
            return super().save_session(app, session, response)
        except Exception as e:
            logger.error(f"Error guardando sesión: {str(e)}")
            response.set_cookie('session', 'fallback-session-id',
                                httponly=True, secure=True, samesite='Lax')
            return response

def configurar_session_fix(app):
    if not isinstance(app, Flask):
        raise TypeError("El argumento 'app' debe ser una instancia de Flask")

    try:
        app.config.update({
            'SESSION_TYPE': 'filesystem',
            'SESSION_FILE_DIR': os.path.join(os.getcwd(), 'flask_session'),
            'SESSION_FILE_MODE': 0o600,
            'SESSION_KEY_PREFIX': 'session:',
            'SESSION_COOKIE_SECURE': False,  # Cambiar a True en producción
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'PERMANENT_SESSION_LIFETIME': 86400,
            'SESSION_USE_SIGNER': True,
            'SESSION_THRESHOLD': 500
        })

        Session(app)

        app.session_interface = CustomSessionInterface(
            app.config['SESSION_FILE_MODE'],
            app.config['SESSION_FILE_DIR'],
            app.config.get('SESSION_THRESHOLD', 500),
            None,  # default_threshold
            app.config['SESSION_USE_SIGNER'],
            app.config['SESSION_KEY_PREFIX'],
            True  # permanent
        )

        logger.info("Configuración de sesiones actualizada correctamente")
        return app

    except Exception as e:
        logger.error(f"Error configurando sesiones: {str(e)}")
        raise
