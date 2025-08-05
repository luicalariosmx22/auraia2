from flask import Blueprint, render_template, request

panel_cliente_contenidos_bp = Blueprint("panel_cliente_contenidos_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/contenidos")

@panel_cliente_contenidos_bp.route("/")
def panel_cliente_contenidos():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_contenidos/index.html", nombre_nora=nombre_nora)
