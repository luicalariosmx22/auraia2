from flask import Blueprint, render_template, request

panel_cliente_agenda_bp = Blueprint("panel_cliente_agenda_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/agenda")

@panel_cliente_agenda_bp.route("/")
def panel_cliente_agenda():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_agenda/index.html", nombre_nora=nombre_nora)
