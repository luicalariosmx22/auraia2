print("🔥 ESTE ES EL APP.PY QUE SE ESTÁ EJECUTANDO")

from flask import Flask, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
import os

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

# ========= REGISTRO DE BLUEPRINTS =========
from clientes.aura.registro.registro_login import registrar_blueprints_login
from clientes.aura.registro.registro_base import registrar_blueprints_base
from clientes.aura.registro.registro_cliente import registrar_blueprints_cliente
from clientes.aura.registro.registro_admin import registrar_blueprints_admin
from clientes.aura.registro.registro_debug import registrar_blueprints_debug
from clientes.aura.registro.registro_dinamico import registrar_blueprints_por_nora
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.webhook import webhook_bp  # Importar el blueprint del webhook

registrar_blueprints_login(app)
registrar_blueprints_base(app)
registrar_blueprints_cliente(app)
registrar_blueprints_admin(app)
registrar_blueprints_debug(app)
registrar_blueprints_por_nora(app, "aura")
app.register_blueprint(panel_chat_bp)

# Verificar si el blueprint 'webhook' ya está registrado
if "webhook" not in app.blueprints:
    app.register_blueprint(webhook_bp)  # Registrar el blueprint del webhook

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
    session.clear()
    return redirect(url_for("login.login_google"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
