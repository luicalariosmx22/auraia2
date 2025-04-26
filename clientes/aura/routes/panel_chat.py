print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint

panel_chat_bp = Blueprint("panel_chat", __name__)

from clientes.aura.routes.panel_chat_routes import *  # Importa SOLO las rutas limpias
