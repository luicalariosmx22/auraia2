import os
import re
from urllib.parse import urljoin

class RutaChecker:
    def __init__(self):
        self.rutas_detectadas = []
        self.rutas_flask = []
        self.resultado_html = "clientes/aura/templates/verificador_rutas_panel.html"

    def analizar_rutas(self, ruta_proyecto):
        for root, _, files in os.walk(ruta_proyecto):
            for archivo in files:
                if archivo.endswith(".py"):
                    self._extraer_rutas_flask(os.path.join(root, archivo))
                elif archivo.endswith(".html"):
                    self._extraer_rutas_html(os.path.join(root, archivo))

    def _extraer_rutas_flask(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()
            rutas = re.findall(r"@[\w_]+\.route\(['\"](/[\w\-/<>]*)", contenido)
            self.rutas_flask.extend(rutas)

    def _extraer_rutas_html(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()
            rutas = re.findall(r'href=["\'](/[^"\']+)["\']', contenido)
            self.rutas_detectadas.extend(rutas)

    def generar_html(self):
        usadas = set(self.rutas_detectadas)
        definidas = set(self.rutas_flask)

        html = "<h2>🔍 Verificador de Rutas y Blueprints</h2>"
        html += f"<p>🧠 Total de rutas usadas en HTML: {len(usadas)}</p>"
        html += f"<p>🛠️ Total de rutas definidas en Flask: {len(definidas)}</p>"

        html += "<h3 style='color: red;'>❌ Rutas usadas en HTML pero NO definidas en Flask</h3><ul>"
        for ruta in usadas - definidas:
            html += f"<li style='color:red'>{ruta}</li>"
        html += "</ul>"

        html += "<h3 style='color: green;'>✅ Rutas definidas y usadas</h3><ul>"
        for ruta in usadas & definidas:
            html += f"<li style='color:green'>{ruta}</li>"
        html += "</ul>"

        html += "<h3>🧱 Todas las rutas definidas en Flask</h3><ul>"
        for ruta in sorted(definidas):
            html += f"<li>{ruta}</li>"
        html += "</ul>"

        os.makedirs(os.path.dirname(self.resultado_html), exist_ok=True)
        with open(self.resultado_html, "w", encoding="utf-8") as f:
            f.write(html)

        return self.resultado_html
