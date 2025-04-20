import os
import re
from typing import List, Dict, Set
import webview
from datetime import datetime  # Importar módulo para manejar fechas
from supabase import create_client, Client
from dotenv import load_dotenv
import sqlite3  # O usa la biblioteca que prefieras para conectarte a la base de datos
import requests  # Importar módulo para realizar solicitudes HTTP

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear cliente de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verificar_ruta_en_servidor(ruta):
    try:
        url = f"https://app.soynoraai.com{ruta}"  # Cambiar localhost por la URL del servidor
        response = requests.head(url, timeout=5)  # Usar HEAD para verificar si la ruta existe
        if response.status_code == 200:
            return "Verificada"
        else:
            return f"No registrada (HTTP {response.status_code})"
    except requests.RequestException as e:
        return f"No registrada (Error: {e})"

class RutaChecker:
    def __init__(self):
        self.resultados = []
        self.blueprints_registrados = set()
        self.rutas_usadas: Set[str] = set()
        self.rutas_definidas: Set[str] = set()
        self.rutas_rotas: List[Dict] = []

    def analizar_rutas(self, carpeta):
        print(f"🔍 Analizando rutas en la carpeta: {carpeta}")
        for root, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                ruta = os.path.join(root, archivo)

                if archivo.endswith(".py"):
                    print(f"📄 Analizando archivo Python: {ruta}")
                    self._analizar_archivo_py(ruta)
                elif archivo.endswith(".html") or archivo.endswith(".js"):
                    print(f"📄 Analizando archivo HTML/JS: {ruta}")
                    self._buscar_usos_en_html_js(ruta)

        # Obtener valores de nombre_nora desde la base de datos
        valores_nombre_nora = obtener_valores_nombre_nora()
        print(f"🔍 Valores obtenidos para nombre_nora: {valores_nombre_nora}")

        # Resolver rutas dinámicas
        rutas_resueltas = set()
        for ruta in self.rutas_usadas:
            if "{{ nombre_nora }}" in ruta:
                for valor in valores_nombre_nora:
                    ruta_resuelta = ruta.replace("{{ nombre_nora }}", valor)
                    rutas_resueltas.add(ruta_resuelta)
                    print(f"🔗 Ruta resuelta: {ruta_resuelta}")
            else:
                rutas_resueltas.add(ruta)

        # Comprobación de rutas usadas pero no definidas
        print("🔎 Verificando si las rutas usadas están registradas en Flask...")
        for ruta, archivo in self.rutas_usadas:  # Desempaquetar la tupla (ruta, archivo)
            ruta_sin_param = ruta.split('?')[0].strip("/")  # Acceder solo a la ruta
            if not any(ruta_sin_param.startswith(r.strip("/")) for r in self.rutas_definidas):
                print(f"🚨 Ruta usada pero no registrada detectada: {ruta}")
                self.rutas_rotas.append({"ruta": ruta, "archivo": archivo})  # Agregar archivo al reporte
            else:
                print(f"✅ Ruta usada y registrada: {ruta}")

    def _analizar_archivo_py(self, ruta_archivo):
        with open(ruta_archivo, encoding="utf-8") as f:
            code = f.read()

        archivo = os.path.basename(ruta_archivo)

        # Blueprints
        blueprints = re.findall(r'Blueprint\(["\'](\w+)["\'].*?url_prefix=["\'](.*?)["\']', code)
        for name, prefix in blueprints:
            print(f"✅ Blueprint detectado: {name} con prefijo {prefix}")
            self.blueprints_registrados.add((name, prefix, archivo))  # Guardar nombre, prefijo y archivo

        # Rutas asociadas a Blueprints
        rutas = re.findall(r'@[\w_]+\.route\(["\'](.*?)["\']', code)
        for ruta in rutas:
            print(f"✅ Ruta detectada en {archivo}: {ruta}")
            self.rutas_definidas.add(ruta.strip("/"))
            self.resultados.append({
                "archivo": archivo,
                "tipo": "Route",
                "ruta": ruta,
                "detalle": f"Ruta declarada"
            })

    def _buscar_usos_en_html_js(self, ruta_archivo):
        with open(ruta_archivo, encoding="utf-8") as f:
            code = f.read()

        archivo = os.path.basename(ruta_archivo)

        # Detectar rutas usadas directamente
        rutas_directas = re.findall(r'(fetch|get|post|axios\.get|axios\.post)\(["\'](\/[^"\']*?)["\']', code)
        for _, ruta in rutas_directas:
            ruta = ruta.replace("{{ nombre_nora }}", "aura")  # Reemplazar {{ nombre_nora }} por 'aura'
            print(f"🔗 Ruta directa detectada en {archivo}: {ruta}")
            self.rutas_usadas.add((ruta, archivo))  # Guardar la ruta junto con el archivo

        # Detectar rutas generadas dinámicamente
        rutas_dinamicas_js = re.findall(r'["\'](\/[^"\']*?)["\']', code)
        for ruta in rutas_dinamicas_js:
            ruta = ruta.replace("{{ nombre_nora }}", "aura")  # Reemplazar {{ nombre_nora }} por 'aura'
            print(f"🔗 Ruta generada dinámicamente detectada en {archivo}: {ruta}")
            self.rutas_usadas.add((ruta, archivo))  # Guardar la ruta junto con el archivo

    def generar_html(self):
        print("📝 Generando reporte HTML...")
        
        # Obtener la fecha y hora actual en formato YYYY-MM-DD_HH-MM-SS
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"reporte_rutas_completo_{fecha_actual}.html"  # Nombre del archivo con la fecha y hora

        html = """
        <html><head><title>🔍 Verificador de Rutas</title>
        <style>
            body { font-family: sans-serif; padding: 1rem; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; }
            th, td { padding: 8px; border: 1px solid #ccc; text-align: left; }
            th { background-color: #f4f4f4; }
            h2 { color: #1a73e8; }
        </style></head><body>
        <h2>📁 Análisis de Rutas y Blueprints</h2>
        """

        # Agrupar rutas por Blueprint
        for name, prefix, archivo in sorted(self.blueprints_registrados):
            html += f"<h3>🔹 Blueprint: {name} (Prefijo: {prefix})</h3>"
            html += f"<p>Declarado en: <strong>{archivo}</strong></p>"
            html += "<table><tr><th>Ruta</th><th>Detalle</th><th>Estado</th></tr>"
            for ruta in self.rutas_definidas:
                if ruta.startswith(prefix.strip("/")):  # Verificar si la ruta pertenece al Blueprint
                    estado = verificar_ruta_en_servidor(ruta)  # Verificar en el servidor remoto
                    color = "green" if "Verificada" in estado else "red"
                    html += f"<tr><td>{ruta}</td><td>Asociada al Blueprint '{name}'</td><td style='color:{color};'>{estado}</td></tr>"
            html += "</table>"

        # Mostrar rutas no asociadas a Blueprints
        html += "<h2>🔸 Rutas no asociadas a ningún Blueprint</h2><table><tr><th>Ruta</th><th>Detalle</th><th>Estado</th></tr>"
        for ruta in self.rutas_definidas:
            if not any(ruta.startswith(prefix.strip("/")) for _, prefix, _ in self.blueprints_registrados):
                estado = verificar_ruta_en_servidor(ruta)  # Verificar en el servidor remoto
                color = "green" if "Verificada" in estado else "red"
                html += f"<tr><td>{ruta}</td><td>No asociada a ningún Blueprint</td><td style='color:{color};'>{estado}</td></tr>"
        html += "</table>"

        html += "</body></html>"

        # Guardar el archivo HTML con la fecha y hora en el nombre
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Reporte HTML generado: {nombre_archivo}")
        return nombre_archivo

# === INTERFAZ ===

class Api:
    def seleccionar_ruta(self):
        print("📂 Botón presionado desde el frontend.")  # Mensaje adicional
        print("🔍 Iniciando selección de carpeta...")  # Mensaje en la consola del backend
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        carpeta = filedialog.askdirectory()

        if not carpeta:
            print("❌ No se seleccionó ninguna carpeta.")  # Mensaje en la consola del backend
            return {"ruta": "Sin seleccionar", "mensaje": "❌ No se seleccionó carpeta"}

        print(f"✅ Carpeta seleccionada: {carpeta}")  # Mensaje en la consola del backend
        checker = RutaChecker()
        checker.analizar_rutas(carpeta)
        html = checker.generar_html()

        # Imprimir los datos enviados al frontend
        print("🔎 Rutas usadas:", checker.rutas_usadas)
        print("🔎 Rutas definidas:", checker.rutas_definidas)
        print("🔎 Rutas rotas:", checker.rutas_rotas)

        return {
            "ruta": carpeta,
            "mensaje": f"✅ Verificación completa. Resultado en: {html}",
            "rutas_usadas": list(checker.rutas_usadas),
            "rutas_definidas": list(checker.rutas_definidas),
            "rutas_rotas": checker.rutas_rotas,
        }

def obtener_valores_nombre_nora():
    try:
        # Realizar la consulta a la tabla configuracion_bot
        response = supabase.table("configuracion_bot").select("nombre_nora").neq("nombre_nora", None).execute()

        # Verificar si la respuesta contiene datos
        if not response.data:
            print("❌ No se encontraron valores en la tabla configuracion_bot.")
            return []

        # Extraer los valores únicos de nombre_nora
        resultados = response.data
        return list({fila["nombre_nora"] for fila in resultados})

    except Exception as e:
        print(f"❌ Error al conectar a Supabase: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Verificador de Rutas Flask")
    
    # Usar la carpeta actual como raíz del proyecto
    carpeta = os.getcwd()  # Obtiene la carpeta actual desde donde se ejecuta el script
    print(f"📂 Carpeta raíz detectada: {carpeta}")

    if not os.path.exists(carpeta):
        print("❌ La carpeta raíz no existe. Por favor, verifica e inténtalo de nuevo.")
    else:
        print(f"✅ Carpeta seleccionada: {carpeta}")
        checker = RutaChecker()
        checker.analizar_rutas(carpeta)
        html = checker.generar_html()
        print(f"✅ Verificación completa. Resultado en: {html}")
