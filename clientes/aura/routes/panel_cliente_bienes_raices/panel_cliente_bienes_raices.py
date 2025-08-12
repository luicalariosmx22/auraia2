from flask import Blueprint, render_template, request

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: Esquemas actualizados automáticamente

panel_cliente_bienes_raices_bp = Blueprint("panel_cliente_bienes_raices_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/bienes_raices")

@panel_cliente_bienes_raices_bp.route("/")
def panel_cliente_bienes_raices():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_bienes_raices/index.html", nombre_nora=nombre_nora)
