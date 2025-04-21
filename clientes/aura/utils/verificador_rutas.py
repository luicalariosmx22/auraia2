import os
import re

class RutaChecker:
    def __init__(self):
        self.rutas_html = []
        self.rutas_flask = []
        self.rutas_no_definidas = []

    def analizar_rutas(self, base_path):
        templates_path = os.path.join(base_path, "templates")
        routes_path = os.path.join(base_path, "routes")

        # Extraer rutas desde plantillas HTML
        self.rutas_html = self.extraer_rutas_desde_templates(templates_path)

        # Extraer rutas desde Flask
        self.rutas_flask = self.extraer_rutas_flask(routes_path)

        # Eliminar duplicados
        self.rutas_html = list({ruta['ruta']: ruta for ruta in self.rutas_html}.values())
        self.rutas_flask = list({ruta['ruta']: ruta for ruta in self.rutas_flask}.values())

        # Identificar rutas no definidas
        self.rutas_no_definidas = [
            ruta for ruta in self.rutas_html if ruta["ruta"] not in [rf["ruta"] for rf in self.rutas_flask]
        ]

    def extraer_rutas_desde_templates(self, templates_path):
        rutas = []
        try:
            for root, _, files in os.walk(templates_path):
                for file in files:
                    if file.endswith(".html"):
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            contenido = f.read()
                            matches = re.findall(r'href="([^"]+)"', contenido)
                            for match in matches:
                                rutas.append({"archivo": file, "ruta": match})
        except Exception as e:
            print(f"❌ Error al extraer rutas desde plantillas: {str(e)}")
        return rutas

    def extraer_rutas_flask(self, routes_path):
        rutas = []
        try:
            for root, _, files in os.walk(routes_path):
                for file in files:
                    if file.endswith(".py"):
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            contenido = f.read()
                            matches = re.findall(r'@(?:app|blueprint)\.route\("([^"]+)"', contenido)
                            for match in matches:
                                rutas.append({"archivo": file, "ruta": match})
        except Exception as e:
            print(f"❌ Error al extraer rutas de Flask: {str(e)}")
        return rutas

    def generar_html(self):
        html = "<h2>🔍 Verificación de Rutas</h2>"
        html += "<h3>Rutas HTML:</h3><ul>"
        for ruta in self.rutas_html:
            html += f"<li>{ruta['ruta']} (Archivo: {ruta['archivo']})</li>"
        html += "</ul>"

        html += "<h3>Rutas Flask:</h3><ul>"
        for ruta in self.rutas_flask:
            html += f"<li>{ruta['ruta']} (Archivo: {ruta['archivo']})</li>"
        html += "</ul>"

        html += "<h3>Rutas No Definidas:</h3><ul>"
        for ruta in self.rutas_no_definidas:
            html += f"<li>{ruta['ruta']} (Archivo: {ruta['archivo']})</li>"
        html += "</ul>"

        return html
