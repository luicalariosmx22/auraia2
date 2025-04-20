from flask import Blueprint, render_template
import os
from clientes.aura.utils.verificador_rutas import RutaChecker

admin_verificador_bp = Blueprint("admin_verificador", __name__)

@admin_verificador_bp.route("/admin/verificador_rutas")
def verificador_rutas_admin():
    # Usa la raíz del proyecto para hacer el análisis
    carpeta_proyecto = os.getcwd()
    checker = RutaChecker()
    checker.analizar_rutas(carpeta_proyecto)
    html_path = checker.generar_html()

    # Leer el HTML generado como string para mostrarlo en el navegador
    with open(html_path, "r", encoding="utf-8") as f:
        contenido_html = f.read()

    return contenido_html
