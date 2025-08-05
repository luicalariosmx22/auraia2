from flask import Blueprint, render_template, request

panel_cliente_call_center_bp = Blueprint("panel_cliente_call_center_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/call_center")

@panel_cliente_call_center_bp.route("/")
def panel_cliente_call_center():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_call_center/index.html", nombre_nora=nombre_nora)
