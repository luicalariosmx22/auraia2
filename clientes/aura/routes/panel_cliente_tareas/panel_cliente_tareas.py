# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/panel_cliente_tareas.py

from flask import Blueprint

panel_cliente_tareas_bp = Blueprint(
    "panel_cliente_tareas", __name__,
    template_folder="../../templates/panel_cliente_tareas"
)

# Solo importa submódulos, sin rutas aquí
from . import tareas_crud
from . import gestionar
from . import plantillas
from . import whatsapp
from . import usuarios_clientes
from . import estadisticas
from . import automatizaciones
from . import verificar
from . import recurrentes