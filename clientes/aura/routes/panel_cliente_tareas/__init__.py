# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/__init__.py

from flask import Blueprint

panel_cliente_tareas_bp = Blueprint(
    "panel_cliente_tareas",
    __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@panel_cliente_tareas_bp.route("/")
def tareas_home():
    return "✅ Módulo de tareas activo"

# Importa los submódulos que registran rutas en este blueprint
from . import (
    tareas_crud,
    plantillas,
    whatsapp,
    usuarios_clientes,
    estadisticas,
    automatizaciones,
    verificar
)
