from flask import Blueprint, render_template, request

panel_cliente_google_maps_bp = Blueprint("panel_cliente_google_maps_bp", __name__)

@panel_cliente_google_maps_bp.route("/")
def panel_cliente_google_maps():
    nombre_nora = request.view_args.get("nombre_nora")
    return render_template("panel_cliente_google_maps/index.html", nombre_nora=nombre_nora)
