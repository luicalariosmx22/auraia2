from flask import Blueprint, render_template, request

panel_cliente_open_table_bp = Blueprint("panel_cliente_open_table_bp", __name__)

@panel_cliente_open_table_bp.route("/")
def panel_cliente_open_table():
    nombre_nora = request.view_args.get("nombre_nora")
    return render_template("panel_cliente_open_table/index.html", nombre_nora=nombre_nora)
