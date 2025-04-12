# app.py

from flask import Flask, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Crear la app Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")

# Configurar sesión en servidor
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ======= BLUEPRINTS ==========
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_cliente import panel_cliente_bp
from clientes.aura.auth.login import login_bp
from clientes.aura.routes.webhook import webhook_bp
# Agrega aquí más blueprints si los necesitas

# ======= REGISTRO DE RUTAS ==========
app.register_blueprint(login_bp)
app.register_blueprint(panel_chat_bp)
app.register_blueprint(panel_cliente_bp)
app.register_blueprint(webhook_bp)

# Ruta raíz
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login_google"))
    if session.get("is_admin"):
        return redirect(url_for("panel_chat_aura.panel_chat"))
    else:
        return redirect(url_for("panel_cliente.panel_cliente"))

# Solo para debug opcional
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login_google"))

# ======= INICIALIZADOR ==========
if __name__ == "__main__":
    app.run(debug=True)
