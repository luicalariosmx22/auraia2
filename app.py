import os
from flask import Flask
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.chat_data import chat_data_bp
from clientes.aura.routes.debug import debug_bp
from clientes.aura.utils.startup_check import inicializar_nora
from clientes.aura.routes.debug_openai import debug_openai_bp

# Inicializar entorno y estructura
inicializar_nora()

app = Flask(__name__, static_url_path="/static", static_folder="clientes/aura/static")

# Registrar rutas del bot Aura
app.register_blueprint(webhook_bp)
app.register_blueprint(panel_chat_bp)
app.register_blueprint(chat_data_bp)
app.register_blueprint(debug_bp)
app.register_blueprint(debug_openai_bp)

@app.route("/")
def home():
    return "Servidor de Aura AI activo."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)