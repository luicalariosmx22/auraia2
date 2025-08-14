from flask import Blueprint, render_template, request

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: Esquemas actualizados automáticamente

panel_cliente_chat_nora_bp = Blueprint("panel_cliente_chat_nora_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/chat_nora")

@panel_cliente_chat_nora_bp.route("/")
def panel_cliente_chat_nora():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_chat_nora/index.html", nombre_nora=nombre_nora)
