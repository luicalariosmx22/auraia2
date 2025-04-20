import os
import re
from flask import current_app


def extraer_rutas_html(html_text):
    """Extrae rutas tipo /algo/{variable} desde href, action o src"""
    patrones = re.findall(r'href=["\'](\/[^"\']+)|action=["\'](\/[^"\']+)|src=["\'](\/[^"\']+)', html_text)
    rutas = set()
    for trio in patrones:
        for r in trio:
            if r and not r.startswith(('http', 'mailto:', '{{', '{%')):  # Evitar externos o jinja
                rutas.add(r.split('?')[0])
    return rutas


def obtener_rutas_flask(app):
    """Obtiene todas las rutas registradas en Flask"""
    rutas = set()
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods:
            rutas.add(rule.rule)
    return rutas


def verificar_rutas_vs_html(app, templates_path="clientes/aura/templates"):
    """Verifica rutas usadas en HTML que no existen en Flask"""
    html_rutas = set()
    for root, _, files in os.walk(templates_path):
        for file in files:
            if file.endswith(".html"):
                with open(f"{root}/{file}", encoding="utf-8") as f:
                    contenido = f.read()
                    html_rutas |= extraer_rutas_html(contenido)

    flask_rutas = obtener_rutas_flask(app)

    # Rutas que no están en Flask y no contienen variables dinámicas
    rutas_sospechosas = []
    for ruta in html_rutas:
        if not any(ruta.startswith(fr) for fr in flask_rutas):
            if "{{" in ruta or "{%" in ruta:  # ignorar bloques jinja
                continue
            rutas_sospechosas.append(ruta)

    return rutas_sospechosas
