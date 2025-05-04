# clientes/aura/routes/panel_chat/__init__.py
from flask import Blueprint
from clientes.aura.routes.panel_chat.vista_panel_chat import *
from clientes.aura.routes.panel_chat.vista_api_chat import *
from clientes.aura.routes.panel_chat.vista_enviar_mensaje import *
from clientes.aura.routes.panel_chat.vista_toggle_ia import *
from clientes.aura.routes.panel_chat.vista_programar_envio import *
from clientes.aura.routes.panel_chat.vista_gestion_etiqueta import *  # Importación agregada
from clientes.aura.routes.panel_chat.blueprint import panel_chat_bp

# Vista principal
panel_chat_bp.add_url_rule("/panel/chat/<nombre_nora>", view_func=panel_chat, methods=["GET"])

# API Chat
panel_chat_bp.add_url_rule("/api/chat/<telefono>", view_func=api_chat, methods=["GET"])
panel_chat_bp.add_url_rule("/api/enviar-mensaje", view_func=api_enviar_mensaje, methods=["POST"])
panel_chat_bp.add_url_rule("/api/toggle-ia/<telefono>", view_func=api_toggle_ia, methods=["POST"])
panel_chat_bp.add_url_rule("/api/programar-envio", view_func=api_programar_envio, methods=["POST"])
panel_chat_bp.add_url_rule("/api/etiqueta/<telefono>", view_func=api_gestion_etiqueta, methods=["POST", "DELETE"])