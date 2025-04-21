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
from clientes.aura.registro.registro_cliente import registrar_blueprints_cliente
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

# Registro base
registrar_blueprints_login(app)
registrar_blueprints_base(app)
registrar_blueprints_cliente(app)
registrar_blueprints_admin(app)
registrar_blueprints_debug(app)

# Registrar el Blueprint admin_verificador_bp
app.register_blueprint(admin_verificador_bp)

# Rutas globales que no dependen de la sesión
if "panel_chat" not in app.blueprints:
    app.register_blueprint(panel_chat_bp)

if "admin_nora_dashboard" not in app.blueprints:
    app.register_blueprint(admin_nora_dashboard_bp)

if "webhook" not in app.blueprints:
    app.register_blueprint(webhook_bp)

if "panel_cliente_etiquetas" not in app.blueprints:
    app.register_blueprint(etiquetas_bp, url_prefix="/panel_cliente_etiquetas")

if "panel_cliente" not in app.blueprints:
    app.register_blueprint(panel_cliente_bp, url_prefix="/panel_cliente")

if "panel_cliente_contactos" not in app.blueprints:
    app.register_blueprint(panel_cliente_contactos_bp, url_prefix="/panel_cliente/contactos")

if "panel_cliente_envios" not in app.blueprints:
    app.register_blueprint(panel_cliente_envios_bp, url_prefix="/panel_cliente/envios")

if "admin_debug_master" not in app.blueprints:
    app.register_blueprint(admin_debug_master_bp, url_prefix="/admin/debug")

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
        return redirect(url_for("panel_cliente.panel_cliente", nombre_nora=session.get("nombre_nora", "aura")))

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
    app.run(debug=False, host="0.0.0.0", port=port)
