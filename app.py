# app.py

from flask import Flask, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Crear la aplicación Flask
app = Flask(
    __name__,
    template_folder='clientes/aura/templates',
    static_folder='clientes/aura/static'
)

# Configurar sesión (fix para Flask-Session)
app.session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ========= BLUEPRINTS OBLIGATORIOS =========
from clientes.aura.auth.login import login_bp
app.register_blueprint(login_bp)  # ✅ Login nunca debe fallar

from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
app.register_blueprint(admin_dashboard_bp)  # ✅ Dashboard debe estar fijo

from clientes.aura.routes.debug_verificar import debug_verificar_bp
app.register_blueprint(debug_verificar_bp)  # ✅ Este blueprint debe estar siempre activo

# ========= IMPORTAR BLUEPRINTS RESTANTES =========
try:
    from clientes.aura.routes.panel_chat import panel_chat_bp
    from clientes.aura.routes.panel_cliente import panel_cliente_bp
    from clientes.aura.routes.webhook import webhook_bp

    from clientes.aura.routes.debug_env import debug_env_bp
    from clientes.aura.routes.debug_google import debug_google_bp
    from clientes.aura.routes.debug_routes import debug_routes_bp

    from clientes.aura.routes.admin_noras import admin_noras_bp
    from clientes.aura.routes.admin_nora import admin_nora_bp

    from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
    from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp

    app.register_blueprint(panel_chat_bp)
    app.register_blueprint(panel_cliente_bp)
    app.register_blueprint(webhook_bp)

    app.register_blueprint(debug_env_bp)
    app.register_blueprint(debug_google_bp)
    app.register_blueprint(debug_routes_bp)

    app.register_blueprint(admin_noras_bp)
    app.register_blueprint(admin_nora_bp)

    app.register_blueprint(panel_cliente_contactos_bp)
    app.register_blueprint(panel_cliente_ia_bp)

except Exception as e:
    with open("boot_error.log", "w", encoding="utf-8") as f:
        f.write("❌ Error al registrar blueprints\n")
        f.write(str(e))

# ========= RUTA INICIAL =========
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard.dashboard_admin"))
    else:
        return redirect(url_for("panel_cliente.panel_cliente"))

# ========= LOGOUT =========
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login_google"))

# ========= INICIO =========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
