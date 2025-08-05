from flask import Blueprint, render_template, request

panel_cliente_airbnb_bp = Blueprint("panel_cliente_airbnb_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/airbnb")

@panel_cliente_airbnb_bp.route("/")
def panel_cliente_airbnb():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_airbnb/index.html", nombre_nora=nombre_nora)
