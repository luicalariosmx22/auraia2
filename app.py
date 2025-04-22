print("🔥 ESTE ES EL APP.PY QUE SE ESTÁ EJECUTANDO")

import os
import uuid
import logging
import engineio
from flask import Flask, session, redirect, url_for
from flask_session import Session
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from clientes.aura.extensions.socketio_instance import socketio

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación Flask
app = Flask(
    __name__,
    template_folder='clientes/aura/templates',
    static_folder='clientes/aura/static'
)
app.session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuración de logs
if not app.debug:
    file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# Reducir los logs de engineio
engineio_logger = logging.getLogger("engineio")
engineio_logger.setLevel(logging.WARNING)

# Inicializar SocketIO
socketio.init_app(app, cors_allowed_origins="*")

# ========= REGISTRO DE BLUEPRINTS =========
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.cobranza import cobranza_bp

# Registro de blueprints
app.register_blueprint(webhook_bp, url_prefix="/api")
app.register_blueprint(panel_chat_bp, url_prefix="/panel_chat")
app.register_blueprint(cobranza_bp, url_prefix="/api/cobranza")

# ========= FUNCIONES AUXILIARES =========
def validar_o_generar_uuid(valor):
    """
    Verifica si el valor es un UUID válido. Si no lo es, genera un nuevo UUID.
    """
    try:
        return str(uuid.UUID(valor))
    except (ValueError, TypeError):
        return str(uuid.uuid4())

# ========= RUTA INICIAL =========
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard.dashboard_admin"))
    else:
        return redirect(url_for("panel_cliente.configuracion_cliente", nombre_nora=session.get("nombre_nora", "aura")))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login_google"))

# ========= INICIALIZACIÓN =========
if __name__ == "__main__":
    try:
        print("📦 Iniciando la aplicación...")
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=False, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
