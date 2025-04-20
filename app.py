print("🔥 ESTE ES EL APP.PY QUE SE ESTÁ EJECUTANDO")

from flask import Flask, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# Cargar variables de entorno
load_dotenv()

# Configurar el modo desarrollador
MODO_DEV = os.getenv("MODO_DEV", "False").lower() == "true"

app = Flask(
    __name__,
    template_folder='clientes/aura/templates',
    static_folder='clientes/aura/static'
)

app.session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if not app.debug:
    file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# ========= REGISTRO DE BLUEPRINTS =========
from clientes.aura.registro.registro_login import registrar_blueprints_login
from clientes.aura.registro.registro_base import registrar_blueprints_base
from clientes.aura.registro.registro_cliente import registrar_blueprints_cliente
from clientes.aura.registro.registro_admin import registrar_blueprints_admin
from clientes.aura.registro.registro_debug import registrar_blueprints_debug
from clientes.aura.registro.registro_dinamico import registrar_blueprints_por_nora
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp  # 👈 NUEVO
from clientes.aura.routes.etiquetas import etiquetas_bp

def registrar_blueprints_cliente(app):
    if app:
        print("Registrando blueprints del cliente...")
    else:
        print("Error: app no está definido.")

registrar_blueprints_login(app)
registrar_blueprints_base(app)
registrar_blueprints_cliente(app)
registrar_blueprints_admin(app)
registrar_blueprints_debug(app)
registrar_blueprints_por_nora(app, "aura")

# Verificar si el blueprint 'panel_chat' ya está registrado
if "panel_chat" not in app.blueprints:
    app.register_blueprint(panel_chat_bp)

# Verificar si el blueprint 'admin_nora_dashboard' ya está registrado
if "admin_nora_dashboard" not in app.blueprints:
    app.register_blueprint(admin_nora_dashboard_bp)  # 👈 NUEVO

# Verificar si el blueprint 'webhook' ya está registrado
if "webhook" not in app.blueprints:
    app.register_blueprint(webhook_bp)

# Verificar si el blueprint 'panel_cliente_etiquetas' ya está registrado
if "panel_cliente_etiquetas" not in app.blueprints:
    app.register_blueprint(etiquetas_bp, url_prefix="/panel/cliente")

# ========= RUTA INICIAL =========
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard.dashboard_admin"))
    else:
        return redirect(url_for("panel_cliente.panel_cliente", nombre_nora="aura"))

@app.route("/logout")
def logout():
    if MODO_DEV:
        print("⚙️ Modo desarrollador activado: Ignorando logout.")
        return redirect(url_for("panel_cliente.panel_cliente", nombre_nora="aura"))
    
    # Comportamiento normal
    session.clear()
    return redirect(url_for("login.login_google"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
