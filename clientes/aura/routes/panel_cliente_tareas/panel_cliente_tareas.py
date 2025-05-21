# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/panel_cliente_tareas.py
# 👉 Archivo principal que define el blueprint y carga los submódulos

from flask import Blueprint

panel_cliente_tareas_bp = Blueprint("panel_cliente_tareas", __name__, template_folder="../../templates/panel_cliente_tareas")

# 🔁 Importa submódulos (cada uno registrará sus propias rutas en este blueprint)
from . import tareas_crud
from . import plantillas
from . import whatsapp
from . import usuarios_clientes
from . import estadisticas
from . import automatizaciones
from . import verificar
