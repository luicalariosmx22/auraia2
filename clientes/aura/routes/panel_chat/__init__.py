# clientes/aura/routes/panel_chat/__init__.py

print("✅ __init__.py del panel_chat cargado correctamente")

from clientes.aura.routes.panel_chat.blueprint import panel_chat_bp

# Solo importamos las vistas para que sus rutas queden registradas automáticamente
from clientes.aura.routes.panel_chat import vista_panel_chat
from clientes.aura.routes.panel_chat import vista_api_chat
from clientes.aura.routes.panel_chat import vista_enviar_mensaje
from clientes.aura.routes.panel_chat import vista_gestion_etiqueta
from clientes.aura.routes.panel_chat import vista_toggle_ia
from clientes.aura.routes.panel_chat import vista_programar_envio
