# ✅ Archivo: clientes/aura/routes/panel_cliente_bienes_raices/panel_cliente_bienes_raices.py
# 👉 Vista base y JSON para mapa (delegando a crud)

from flask import Blueprint, render_template, request, jsonify
from .crud import get_geojson_propiedades

panel_cliente_bienes_raices_bp = Blueprint(
    "panel_cliente_bienes_raices_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/bienes_raices"
)

@panel_cliente_bienes_raices_bp.route("/")

def panel_cliente_bienes_raices_index():
    # Extraer nombre_nora de la URL de forma robusta (patrón oficial de otros módulos)
    from flask import request
    nombre_nora = request.path.split("/")[2]
    return render_template(
        "panel_cliente_bienes_raices/index.html",
        nombre_nora=nombre_nora,
        modulo_activo="bienes_raices"
    )

@panel_cliente_bienes_raices_bp.route("/mapa/datos", methods=["GET"])
def mapa_datos():
    # Extraer nombre_nora de la URL de forma robusta (patrón oficial de otros módulos)
    from flask import request
    nombre_nora = request.path.split("/")[2]
    filtros = {
        "operacion": request.args.get("operacion"),
        "ciudad": request.args.get("ciudad"),
        "texto": request.args.get("q"),
    }
    data = get_geojson_propiedades(nombre_nora, filtros)
    return jsonify(data)
