# clientes/aura/debug/debug_archivos.py

import os
from flask import Blueprint, render_template_string

debug_archivos_bp = Blueprint("debug_archivos", __name__)

ARCHIVOS_REQUERIDOS = [
    "clientes/aura/database/bot_data.json",
    "clientes/aura/database/categorias.json",
    "clientes/aura/database/contactos.json",
    "clientes/aura/database/config.json",
]

@debug_archivos_bp.route("/debug/archivos")
def verificar_archivos():
    resultados = []

    for archivo in ARCHIVOS_REQUERIDOS:
        nombre = os.path.basename(archivo)
        if os.path.exists(archivo):
            resultados.append((nombre, "✅ Encontrado"))
        else:
            resultados.append((nombre, "❌ No encontrado"))

    # Plantilla HTML simple para mostrar los resultados (puedes luego mover esto a un template si prefieres)
    html = """
    <h3>🗃️ Verificación de Archivos Requeridos</h3>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Archivo</th><th>Estado</th></tr>
        {% for archivo, estado in resultados %}
            <tr>
                <td>{{ archivo }}</td>
                <td>{{ estado }}</td>
            </tr>
        {% endfor %}
    </table>
    """

    return render_template_string(html, resultados=resultados)
