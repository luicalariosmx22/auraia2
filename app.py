print("🔥 ESTE ES EL APP.PY QUE SE ESTÁ EJECUTANDO")

import os
import uuid
import logging
from flask import Flask, session, redirect, url_for, request, jsonify
from flask_session import Session
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.utils.supabase import supabase
from clientes.aura.extensions.socketio_instance import socketio
from werkzeug.serving import WSGIRequestHandler

class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        # Solo filtra los logs que contienen '200 -'
        return ' 200 -' not in record.getMessage()

# Filtrar solo los logs de werkzeug
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(WerkzeugFilter())

# Redirigir logs de polling a archivo separado
socketio_log = logging.getLogger('socketio_polling')
socketio_log.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/socketio_polling.log", maxBytes=100000, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
socketio_log.addHandler(handler)

# Cargar variables de entorno
load_dotenv()

# Silenciar logs de Twilio
logging.getLogger("twilio.http_client").setLevel(logging.WARNING)
app = Flask(
    __name__,
    template_folder='clientes/aura/templates',
    static_folder='clientes/aura/static'
)

app.session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Inicializar SocketIO con la aplicación Flask
socketio.init_app(app, cors_allowed_origins="*")

# Logger en producción
if not app.debug:
    file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# ========= REGISTRO DE BLUEPRINTS =========
from clientes.aura.registro.registro_login import registrar_blueprints_login
from clientes.aura.registro.registro_base import registrar_blueprints_base
from clientes.aura.registro.registro_admin import registrar_blueprints_admin
from clientes.aura.registro.registro_debug import registrar_blueprints_debug
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
from clientes.aura.routes.etiquetas import etiquetas_bp
from clientes.aura.routes.panel_cliente import panel_cliente_bp
from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
from clientes.aura.routes.admin_verificador_rutas import admin_verificador_bp
from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
from clientes.aura.routes.admin_noras import admin_noras_bp
from clientes.aura.routes.admin_debug_master import admin_debug_master_bp
from clientes.aura.registro.registro_dinamico import registrar_blueprints_por_nora
from clientes.aura.routes.admin_nora import admin_nora_bp
from clientes.aura.routes.cliente_nora import cliente_nora_bp
from clientes.aura.routes.panel_chat.vista_api_chat import vista_api_chat_bp
from clientes.aura.routes.panel_chat.vista_panel_chat import vista_panel_chat_bp
from clientes.aura.routes.panel_chat.vista_enviar_mensaje import vista_enviar_mensaje_bp
from clientes.aura.routes.panel_chat.vista_toggle_ia import vista_toggle_ia_bp
from clientes.aura.routes.cobranza import cobranza_bp

registrar_blueprints_login(app)
registrar_blueprints_base(app)
registrar_blueprints_admin(app)
registrar_blueprints_debug(app)

blueprints_estaticos = [
    (admin_verificador_bp, None),
    (panel_chat_bp, "/panel_chat"),
    (vista_api_chat_bp, None),
    (vista_panel_chat_bp, None),
    (vista_enviar_mensaje_bp, None),
    (vista_toggle_ia_bp, None),
    (admin_nora_dashboard_bp, None),
    (webhook_bp, None),
    (etiquetas_bp, "/panel_cliente_etiquetas"),
    (panel_cliente_bp, "/panel_cliente"),
    (panel_cliente_contactos_bp, "/panel_cliente/contactos"),
    (panel_cliente_envios_bp, "/panel_cliente/envios"),
    (admin_debug_master_bp, "/admin/debug"),
    (admin_nora_bp, "/admin/nora"),
    (cliente_nora_bp, "/panel_cliente")
]

for blueprint, prefix in blueprints_estaticos:
    if blueprint.name not in app.blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)

app.register_blueprint(cobranza_bp, url_prefix="/api")

try:
    response = supabase.table("configuracion_bot").select("nombre_nora").execute()
    nombre_noras = [n["nombre_nora"] for n in response.data] if response.data else []

    for nombre in nombre_noras:
        registrar_blueprints_por_nora(app, nombre)
except Exception as e:
    app.logger.error(f"Error al registrar Noras dinámicas: {e}")

# ========= FUNCIONES AUXILIARES =========
def validar_o_generar_uuid(valor):
    try:
        return str(uuid.UUID(valor))
    except (ValueError, TypeError):
        return str(uuid.uuid4())

def registrar_rutas_en_supabase():
    rutas = []
    for rule in app.url_map.iter_rules():
        rutas.append({
            "id": validar_o_generar_uuid(""),
            "ruta": rule.rule,
            "blueprint": rule.endpoint.split(".")[0] if "." in rule.endpoint else "default",
            "metodo": ", ".join(rule.methods - {"HEAD", "OPTIONS"}),
            "registrado_en": datetime.now().isoformat()
        })
    try:
        response = supabase.table("rutas_registradas").insert(rutas).execute()
    except Exception as e:
        app.logger.error(f"Error al registrar rutas en Supabase: {str(e)}")

# Convertir iterador a lista para calcular la longitud
app.logger.info(f"📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")

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

@app.route('/debug_info', methods=['GET'])
def debug_info():
    return jsonify({
        "rutas_registradas": [rule.rule for rule in app.url_map.iter_rules()],
        "estado": "OK",
    })

@app.before_request
def log_polling_requests():
    if request.path.startswith('/socket.io') and request.args.get('transport') == 'polling':
        socketio_log.info(f"{request.remote_addr} - {request.method} {request.full_path}")

if __name__ == "__main__":
    try:
        registrar_rutas_en_supabase()
        generar_html_rutas(app, output_path="clientes/aura/templates/debug_rutas.html")
    except Exception as e:
        app.logger.error(f"Error crítico: {str(e)}")

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=False, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
