from flask import Blueprint, render_template, request, jsonify

# �️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: Esquemas actualizados automáticamente

from clientes.aura.utils.sincronizar_ical import sincronizar_ical

panel_cliente_airbnb_bp = Blueprint(
    "panel_cliente_airbnb_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/airbnb"
)

@panel_cliente_airbnb_bp.route("/")
def panel_cliente_airbnb():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_airbnb/index.html", nombre_nora=nombre_nora)

@panel_cliente_airbnb_bp.route("/sincronizar", methods=["POST"])
def sincronizar_reservas_ical():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    data = request.get_json()

    url_ical = data.get("url_ical")
    fuente = data.get("fuente", "airbnb")

    if not url_ical:
        return jsonify({"error": "Falta el parámetro url_ical"}), 400

    try:
        sincronizar_ical(nombre_nora, url_ical, fuente)
        return jsonify({"ok": True, "mensaje": "Sincronización completada."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
