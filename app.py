import os
from flask import Flask, session, render_template, redirect, url_for
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar módulos del proyecto Aura
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.chat_data import chat_data_bp
from clientes.aura.routes.debug import debug_bp
from clientes.aura.routes.debug_openai import debug_openai_bp
from clientes.aura.auth.google_login import google_login_bp
from clientes.aura.routes.debug_login import debug_login_bp
from clientes.aura.routes.debug_google import debug_google_bp
from clientes.aura.utils.startup_check import inicializar_nora

# Inicializar entorno y estructura
inicializar_nora()

# Crear app Flask
app = Flask(__name__, static_url_path="/static", static_folder="clientes/aura/static")
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "clave-secreta-fallback"

# Registrar Blueprints
app.register_blueprint(webhook_bp)
app.register_blueprint(panel_chat_bp)
app.register_blueprint(chat_data_bp)
app.register_blueprint(debug_bp)
app.register_blueprint(debug_openai_bp)
app.register_blueprint(google_login_bp)
app.register_blueprint(debug_login_bp)
app.register_blueprint(debug_google_bp)

# Ruta raíz
@app.route("/")
def home():
    if "user" in session:
        if session.get("is_admin"):
            return redirect(url_for("panel_chat.panel_chat"))
        else:
            return redirect(url_for("panel_chat.panel_cliente"))
    return render_template("login.html")

# Iniciar servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
