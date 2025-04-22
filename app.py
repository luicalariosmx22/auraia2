print("🔥 ESTE ES EL APP.PY QUE SE ESTÁ EJECUTANDO")

import os
import uuid
import logging  # Importación necesaria para evitar el NameError
from flask import Flask, session, redirect, url_for, request, jsonify
from flask_session import Session
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from clientes.aura.utils.debug_rutas import generar_html_rutas  # Importación correcta
from clientes.aura.utils.supabase import supabase
from clientes.aura.extensions.socketio_instance import socketio  # Importar instancia de SocketIO

# Redirigir logs de polling a archivo separado
socketio_log = logging.getLogger('socketio_polling')
socketio_log.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/socketio_polling.log", maxBytes=100000, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
socketio_log.addHandler(handler)

# Cargar variables de entorno
load_dotenv()

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
socketio.init_app(app, cors_allowed_origins="*")  # Configuración de WebSockets

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

# Nuevos blueprints del módulo Panel Chat
from clientes.aura.routes.panel_chat.vista_api_chat import vista_api_chat_bp
from clientes.aura.routes.panel_chat.vista_panel_chat import vista_panel_chat_bp
from clientes.aura.routes.panel_chat.vista_enviar_mensaje import vista_enviar_mensaje_bp
from clientes.aura.routes.panel_chat.vista_toggle_ia import vista_toggle_ia_bp

# Blueprint de cobranza
from clientes.aura.routes.cobranza import cobranza_bp

# Registro base
registrar_blueprints_login(app)
registrar_blueprints_base(app)
registrar_blueprints_admin(app)
registrar_blueprints_debug(app)

# Registro de blueprints estáticos
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

# Registrar el blueprint de cobranza
app.register_blueprint(cobranza_bp, url_prefix="/api")

# 🔁 Registro dinámico de todas las Noras desde Supabase
try:
    response = supabase.table("configuracion_bot").select("nombre_nora").execute()
    nombre_noras = [n["nombre_nora"] for n in response.data] if response.data else []

    print(f"🔁 Registrando dinámicamente las siguientes Noras: {nombre_noras}")
    for nombre in nombre_noras:
        registrar_blueprints_por_nora(app, nombre)
except Exception as e:
    print(f"❌ Error al registrar Noras dinámicas: {e}")

# ========= FUNCIONES AUXILIARES =========
def validar_o_generar_uuid(valor):
    """
    Verifica si el valor es un UUID válido. Si no lo es, genera un nuevo UUID.
    """
    try:
        return str(uuid.UUID(valor))
    except (ValueError, TypeError):
        return str(uuid.uuid4())

def registrar_rutas_en_supabase():
    """
    Registra las rutas activas de la aplicación en Supabase.
    """
    rutas = []
    for rule in app.url_map.iter_rules():
        rutas.append({
            "id": validar_o_generar_uuid(""),  # Esto no es necesario si Supabase genera automáticamente el UUID
            "ruta": rule.rule,
            "blueprint": rule.endpoint.split(".")[0] if "." in rule.endpoint else "default",  # Extraer el blueprint del endpoint
            "metodo": ", ".join(rule.methods - {"HEAD", "OPTIONS"}),  # Excluir métodos no relevantes
            "registrado_en": datetime.now().isoformat()  # Esto no es necesario si Supabase usa `now()`
        })
    try:
        response = supabase.table("rutas_registradas").insert(rutas).execute()
        print(f"✅ Rutas registradas en Supabase: {response}")
    except Exception as e:
        print(f"❌ Error al registrar rutas en Supabase: {str(e)}")

# Validar que las rutas estén correctamente registradas
print("📋 Rutas registradas en la aplicación:")
for rule in app.url_map.iter_rules():
    print(f"Ruta: {rule.rule} - Métodos: {', '.join(rule.methods)} - Endpoint: {rule.endpoint}")

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

# ========= INICIALIZACIÓN =========
if __name__ == "__main__":
    try:
        print("📦 Registrando rutas activas en Supabase...")
        registrar_rutas_en_supabase()

        print("📄 Generando HTML de rutas...")
        generar_html_rutas(app, output_path="clientes/aura/templates/debug_rutas.html")  # Uso correcto
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=False, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)  # Actualizado con allow_unsafe_werkzeug
