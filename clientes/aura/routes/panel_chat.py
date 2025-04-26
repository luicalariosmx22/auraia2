print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint

# Registrar el Blueprint principal
panel_chat_bp = Blueprint("panel_chat", __name__)

# Importar las rutas para activarlas
from clientes.aura.routes.panel_chat_routes import *  # noqa
