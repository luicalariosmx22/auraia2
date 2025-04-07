from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_socketio import SocketIO
from routes.main import main_bp as main_blueprint
from routes.categorias import categorias_bp as categorias_blueprint
from routes.respuestas import respuestas_bp as respuestas_blueprint
from routes.webhook import webhook as webhook_blueprint
from routes.whatsapp import whatsapp_bp as whatsapp_blueprint
from routes.panel_chat import panel_chat_bp as panel_chat_blueprint
from routes.error_panel import error_panel_bp  # 🔹 Agregado
from utils.config import cargar_configuracion
from socketio_handlers import register_socketio_handlers
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

# Verificación crítica de directorios
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)
    print(f"✅ Directorio templates creado en: {TEMPLATES_DIR}")

# Inicializa la aplicación Flask
app = Flask(__name__,
            template_folder=TEMPLATES_DIR,
            static_folder=os.path.join(BASE_DIR, 'static'))

# Configuraciones
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY') or cargar_configuracion().get('secret_key', 'default_secret'),
    TEMPLATES_AUTO_RELOAD=True
)

# Inicializar CSRF y SocketIO
csrf = CSRFProtect(app)
socketio = SocketIO(app, cors_allowed_origins="*")
print("🔧 SocketIO inicializado y a la espera de eventos...")

# CSRF en Jinja
@app.context_processor
def inject_csrf():
    return dict(csrf_token=generate_csrf)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    template_path = os.path.join(app.template_folder, 'login.html')

    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"❌ No se encontró login.html en: {template_path}\n"
            f"📁 Directorio de templates actual: {app.template_folder}"
        )

    if request.method == 'POST':
        password = request.form.get('password')
        expected_password = os.getenv('ADMIN_PASSWORD', 'tu_contraseña_secreta')
        if password == expected_password:
            session['logged_in'] = True
            return redirect(url_for('panel_chat.panel_chat'))
        flash('Contraseña incorrecta', 'error')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Middleware para proteger rutas
@app.before_request
def require_login():
    allowed_routes = ['login', 'static', 'webhook']
    if request.endpoint and request.endpoint.split('.')[0] not in allowed_routes and not session.get('logged_in'):
        return redirect(url_for('login'))

# Registro de Blueprints
blueprints = [
    (main_blueprint, None),
    (categorias_blueprint, None),
    (respuestas_blueprint, None),
    (webhook_blueprint, {'url_prefix': '/webhook'}),
    (whatsapp_blueprint, None),
    (panel_chat_blueprint, None),
    (error_panel_bp, None)  # 🔹 Panel de errores
]

for bp, options in blueprints:
    app.register_blueprint(bp, **(options or {}))

# Excepciones CSRF para ciertas rutas
csrf.exempt(webhook_blueprint)
csrf.exempt(panel_chat_blueprint)

# Registrar SocketIO handlers
register_socketio_handlers(socketio)

# Verificación final
print("\n--- ✅ Configuración Final ---")
print(f"📂 Directorio de templates: {app.template_folder}")
print(f"🔍 Ruta esperada para login.html: {os.path.join(app.template_folder, 'login.html')}")
print(f"📄 ¿Existe login.html? {'Sí' if os.path.exists(os.path.join(app.template_folder, 'login.html')) else 'No'}\n")

# Iniciar servidor
if __name__ == '__main__':
    socketio.run(app,
                 debug=True,
                 host='0.0.0.0',
                 port=5000)
