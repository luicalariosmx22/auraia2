from flask import Blueprint, render_template_string
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.utils.verificador_rutas_runtime import verificar_rutas_vs_html

debug_verificador_bp = Blueprint("debug_verificador", __name__)

@debug_verificador_bp.route("/debug/verificar")
def verificar_todo():
    from flask import current_app as app
    html_rutas = generar_html_rutas(app)
    rutas_html_no_definidas = verificar_rutas_vs_html(app)

    html_extra = "<h2>⚠️ Rutas HTML no definidas en Flask:</h2><ul>"
    for ruta in rutas_html_no_definidas:
        html_extra += f"<li>{ruta}</li>"
    html_extra += "</ul>"

    return html_rutas.replace("</body>", html_extra + "</body>")
