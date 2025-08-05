from flask import Blueprint, render_template, request

panel_cliente_lading_pages_bp = Blueprint("panel_cliente_lading_pages_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/lading_pages")

@panel_cliente_lading_pages_bp.route("/")
def panel_cliente_lading_pages():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_lading_pages/index.html", nombre_nora=nombre_nora)
