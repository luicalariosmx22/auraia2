# app.py

from flask import Flask, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Crear la aplicación Flask y especificar la carpeta de plantillas
app = Flask(__name__, template_folder='clientes/aura/templates')
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")

# Configurar la sesión en el servidor
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ========= IMPORTAR BLUEPRINTS =========
try:
    from clientes.aura.routes.panel_chat import panel_chat_bp
    from clientes.aura.routes.panel_cliente import panel_cliente_bp
    from clientes.aura.auth.login import login_bp
    from clientes.aura.routes.webhook import webhook_bp
    from clientes.aura.routes.debug_verificar import debug_verificar_bp  # 👈 NUEVO

    # ========= REGISTRAR BLUEPRINTS =========
    app.register_blueprint(login_bp)
    app.register_blueprint(panel_chat_bp)
    app.register_blueprint(panel_cliente_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(debug_verificar_bp)

except Exception as e:
    # Esto ayuda a que si Railway levanta el app.py y algo falla, lo puedas ver en el log de boot
    with open("boot_error.log", "w") as f:
        f.write("❌ Error al registrar blueprints\n")
        f.write(str(e))

# ========= RUTA INICIAL =========
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("panel_chat.panel_chat"))
    else:
        return redirect(url_for("panel_cliente.panel_cliente"))

# ========= LOGOUT =========
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login_google"))

# ========= INICIO =========
if __name__ == "__main__":
    # Este puerto es solo para ejecución local
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
