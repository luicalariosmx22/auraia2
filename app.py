from flask import Flask, render_template, request, redirect, url_for, session, flash 
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_socketio import SocketIO
from routes.main import main_bp as main_blueprint
from routes.categorias import categorias_bp as categorias_blueprint
from routes.respuestas import respuestas_bp as respuestas_blueprint
from routes.webhook import webhook as webhook_blueprint
from routes.whatsapp import whatsapp_bp as whatsapp_blueprint
from routes.panel_chat import panel_chat_bp as panel_chat_blueprint
from routes.error_panel import panel_errores_bp as error_panel_bp
from utils.config import cargar_configuracion
from socketio_handlers import register_socketio_handlers
from dotenv import load_dotenv
from routes.etiquetas import etiquetas_bp
from routes.api_mensajes import api_mensajes  # al inicio

import os
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables desde .env
load_dotenv()

# Verificación crítica de directorios
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

logger.info(f"📂 Directorio de templates: {TEMPLATES_DIR}")
logger.info(f"📂 Directorio static: {STATIC_DIR}")

# ✅ Crear archivos esenciales si no existen
archivos_requeridos = {
    "bot_data.json": "{}",
    "categorias.json": "[]"
}

for archivo, contenido in archivos_requeridos.items():
    ruta = os.path.join(BASE_DIR, archivo)
    if not os.path.exists(ruta):
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        logger.warning(f"⚠️ Archivo creado automáticamente: {archivo}")

# Inicializa la aplicación Flask
app = Flask(__name__,
            template_folder=TEMPLATES_DIR,
            static_folder=STATIC_DIR)

# Configuraciones esenciales para producción
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', cargar_configuracion().get('secret_key', 'fallback_secret_key')),
    TEMPLATES_AUTO_RELOAD=os.getenv('FLASK_ENV') == 'development',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600  # 1 hora
)

# Inicializar CSRF y SocketIO
csrf = CSRFProtect(app)
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    logger=logger,
                    engineio_logger=os.getenv('FLASK_ENV') == 'development')

# ⚠️ Desactivar CSRF completo para el blueprint del webhook
csrf.exempt(webhook_blueprint)

# También puedes dejar esta línea si deseas seguir excluyendo esa ruta específica
csrf._exempt_views.add('panel_chat.panel_chat')

# Inyectar CSRF en templates
@app.context_processor
def inject_csrf():
    return dict(csrf_token=generate_csrf)

# Sistema de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    template_path = os.path.join(app.template_folder, 'login.html')

    if not os.path.exists(template_path):
        logger.error(f"Archivo login.html no encontrado en: {template_path}")
        return "Error de configuración: falta login.html", 500

    if request.method == 'POST':
        password = request.form.get('password')
        expected_passwords = [
            os.getenv('ADMIN_PASSWORD'),
            os.getenv('LOGIN_PASSWORD'),
            cargar_configuracion().get('admin_password')
        ]
        if password in expected_passwords:
            session['logged_in'] = True
            session['logueado'] = True  # ✅ necesario para acceder a main.index
            session.permanent = True
            return redirect(url_for('main.index'))  # ✅ redirige al panel principal

        flash('Credenciales inválidas', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ✅ Middleware de autenticación
@app.before_request
def require_login():
    if request.path.startswith('/webhook'):
        return  # Permitir POST del webhook

    allowed_paths = [
        '/login',
        '/logout',
        '/healthcheck',
        '/static/'
    ]

    if any(request.path.startswith(p) for p in allowed_paths):
        return

    if not session.get('logged_in'):
        return redirect(url_for('login'))

# Registro de blueprints
blueprints = [
    (main_blueprint, None),
    (categorias_blueprint, None),
    (respuestas_blueprint, None),
    (webhook_blueprint, {'url_prefix': '/webhook'}),
    (whatsapp_blueprint, None),
    (panel_chat_blueprint, None),
    (error_panel_bp, None),
    (etiquetas_bp, None),
    (api_mensajes, None)  # ✅ última línea SIN coma después
]  # <== importante este cierre



for bp, options in blueprints:
    try:
        app.register_blueprint(bp, **(options or {}))
        logger.info(f"✅ Blueprint registrado: {bp.name}")
    except Exception as e:
        logger.error(f"❌ Error registrando {bp.name}: {str(e)}")
        raise

# Registrar eventos de SocketIO
register_socketio_handlers(socketio)

# Healthcheck
@app.route('/healthcheck')
def healthcheck():
    return "OK", 200

# Iniciar servidor
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"\n--- 🚀 Iniciando servidor en modo {'DESARROLLO' if debug_mode else 'PRODUCCIÓN'} ---")
    logger.info(f"🔌 SocketIO habilitado en: ws://0.0.0.0:{port}")
    logger.info(f"🌐 Accesible en: http://0.0.0.0:{port}")

    socketio.run(app,
                 host='0.0.0.0',
                 port=port,
                 debug=debug_mode,
                 use_reloader=debug_mode,
                 allow_unsafe_werkzeug=debug_mode)
