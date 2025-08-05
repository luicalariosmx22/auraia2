from flask import Blueprint, render_template, request

panel_cliente_redes_sociales_bp = Blueprint("panel_cliente_redes_sociales_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/redes_sociales")

@panel_cliente_redes_sociales_bp.route("/")
def panel_cliente_redes_sociales():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_redes_sociales/index.html", nombre_nora=nombre_nora)
