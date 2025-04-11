from flask import Flask
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.chat_data import chat_data_bp

app = Flask(__name__, static_url_path="/static", static_folder="clientes/aura/static")

# Registrar rutas de Aura
app.register_blueprint(webhook_bp)
app.register_blueprint(panel_chat_bp)
app.register_blueprint(chat_data_bp)

# Ruta raíz opcional
@app.route("/")
def home():
    return "Servidor activo"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
