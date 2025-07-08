from flask import Blueprint, Response
from clientes.aura.utils.debug_rutas import generar_html_rutas

debug_rutas_bp = Blueprint("debug_rutas", __name__)

@debug_rutas_bp.route("/debug/rutas", methods=["GET"])
def mostrar_rutas():
    """
    Muestra las rutas registradas en la aplicación en formato HTML.
    
    Returns:
        Response: Respuesta HTTP con el HTML generado.
    """
    html = generar_html_rutas()
    return Response(html, content_type="text/html")