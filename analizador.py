import os
import re
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
import pdfkit
import tkinter as tk
from tkinter import filedialog
import openai  # Cliente de OpenAI para usar GPT
from dotenv import load_dotenv  # Cargar variables de entorno desde .env
from supabase import create_client, Client  # Biblioteca para conectarse a Supabase
from datetime import datetime  # Para agregar la fecha al nombre del archivo

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configura tu clave de API de OpenAI desde la variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("No se encontró la clave de API de OpenAI. Configúrala en el archivo .env.")

# Configurar conexión a Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("No se encontraron las credenciales de Supabase. Configúralas en el archivo .env.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AnalizadorProyecto:
    def __init__(self, base_path: str, file_extension: str):
        self.base_path = base_path
        self.file_extension = file_extension
        self.reporte = []
        self.categorias = {}

    def analizar_archivos(self):
        """Recorre todos los archivos con la extensión seleccionada en el proyecto y analiza su contenido."""
        print("Iniciando análisis de archivos...")
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(self.file_extension):
                    filepath = os.path.join(root, file)
                    print(f"Analizando archivo: {filepath}")
                    self.analizar_archivo(filepath)
        print("Análisis de archivos completado.")

    def analizar_archivo(self, filepath: str):
        """Analiza un archivo y extrae la información solicitada."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Nombre del archivo
        nombre = os.path.basename(filepath)

        # 2. Usar IA para inferir el propósito del archivo
        print(f"Inferiendo propósito del archivo: {nombre}")
        proposito = self.inferir_proposito_ia(content)

        # 3. Rutas registradas (solo para .py)
        rutas = self.extraer_rutas(content) if self.file_extension == ".py" else []

        # 4. Archivos CSS necesarios (solo para .html)
        css_files = self.extraer_archivos_css(content) if self.file_extension == ".html" else []

        # 5. Archivos HTML necesarios (solo para .py)
        html_files = self.extraer_archivos_html(content) if self.file_extension == ".py" else []

        # 6. Tablas y columnas que busca (solo para .py)
        tablas_columnas = self.extraer_tablas_columnas(content)

        # 7. Archivos .py que usa (solo para .py)
        archivos_py = self.extraer_imports(content) if self.file_extension == ".py" else []

        # Excluir resultados vacíos
        if not (rutas or css_files or html_files or tablas_columnas or archivos_py):
            print(f"Archivo {nombre} no tiene información relevante. Excluido del reporte.")
            return

        # Agregar al reporte
        self.reporte.append({
            "nombre": nombre,
            "proposito": proposito,
            "rutas": rutas,
            "css_files": css_files,
            "html_files": html_files,
            "tablas_columnas": tablas_columnas,
            "archivos_py": archivos_py,
        })

        # Agregar a la categoría correspondiente
        categoria = self.clasificar_categoria(proposito)
        if categoria not in self.categorias:
            self.categorias[categoria] = []
        self.categorias[categoria].append({
            "nombre": nombre,
            "proposito": proposito,
            "rutas": rutas,
            "css_files": css_files,
            "html_files": html_files,
            "tablas_columnas": tablas_columnas,
            "archivos_py": archivos_py,
        })

    def inferir_proposito_ia(self, content: str) -> str:
        """Usa IA para inferir el propósito del archivo."""
        try:
            prompt = (
                "Analiza el siguiente código y describe brevemente su propósito. "
                "Proporciona una descripción clara y concisa:\n\n"
                f"{content[:2000]}"  # Limitar el contenido enviado para evitar exceder el límite de tokens
            )
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Cambia a "gpt-4" si tienes acceso
                messages=[
                    {"role": "system", "content": "Eres un asistente que analiza código y describe su propósito."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.5,
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error al usar IA para analizar el archivo: {e}")
            return "No se pudo determinar el propósito del archivo."

    def clasificar_categoria(self, proposito: str) -> str:
        """Clasifica el archivo en una categoría basada en su propósito."""
        if "etiquetas" in proposito.lower():
            return "Etiquetas"
        elif "ruta" in proposito.lower() or "endpoint" in proposito.lower():
            return "Rutas"
        elif "html" in proposito.lower():
            return "HTML"
        elif "css" in proposito.lower():
            return "CSS"
        elif "base de datos" in proposito.lower() or "tabla" in proposito.lower():
            return "Base de Datos"
        else:
            return "Otros"

    def extraer_rutas(self, content: str) -> List[str]:
        """Extrae las rutas registradas en el archivo."""
        rutas = re.findall(r"@app\.route\(['\"](.*?)['\"]", content)
        return rutas

    def extraer_archivos_css(self, content: str) -> List[str]:
        """Busca referencias a archivos CSS en el contenido."""
        css_files = re.findall(r"href=['\"](.*?\.css)['\"]", content)
        return css_files

    def extraer_archivos_html(self, content: str) -> List[str]:
        """Busca referencias a archivos HTML en el contenido."""
        html_files = re.findall(r"render_template\(['\"](.*?\.html)['\"]", content)
        return html_files

    def extraer_tablas_columnas(self, content: str) -> List[Dict[str, str]]:
        """Busca referencias a tablas y columnas en el contenido y verifica si existen en Supabase."""
        tablas_columnas = []
        for match in re.findall(r"supabase\.from_\(['\"](.*?)['\"]\).*?\.select\(['\"](.*?)['\"]", content):
            tabla, columnas = match
            columnas = [col.strip() for col in columnas.split(",")]

            # Verificar si la tabla existe en Supabase
            print(f"Verificando existencia de la tabla '{tabla}' en Supabase...")
            response = supabase.table(tabla).select("*").limit(1).execute()
            if response.status_code == 200:
                tablas_columnas.append({"tabla": tabla, "columnas": columnas})
            else:
                print(f"La tabla '{tabla}' no existe en Supabase.")

        return tablas_columnas

    def extraer_imports(self, content: str) -> List[str]:
        """Busca los archivos .py importados en el archivo."""
        imports = re.findall(r"from (.*?) import|import (.*?)", content)
        archivos_py = [imp[0] or imp[1] for imp in imports if imp[0] or imp[1]]
        return archivos_py

    def generar_html(self, output_file: str = "reporte_proyecto.html"):
        """Genera un reporte en formato HTML agrupado por categorías."""
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("template_reporte.html")

        html_content = template.render(categorias=self.categorias)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Reporte HTML generado en: {output_file}")

    def generar_pdf(self, html_file: str = "reporte_proyecto.html"):
        """Genera un reporte en formato PDF a partir del HTML."""
        try:
            # Usar rutas absolutas
            html_file = os.path.abspath(html_file)

            # Obtener el nombre de la carpeta y la fecha actual
            carpeta_nombre = os.path.basename(self.base_path)
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            output_file = os.path.abspath(f"reporte_{carpeta_nombre}_{fecha_actual}.pdf")

            # Configuración de wkhtmltopdf
            config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
            options = {
                'enable-local-file-access': None,  # Permite acceso a archivos locales
                'quiet': ''  # Modo detallado para depuración
            }

            # Generar PDF
            pdfkit.from_file(html_file, output_file, configuration=config, options=options)
            print(f"Reporte PDF generado en: {output_file}")
        except Exception as e:
            print(f"Error al generar el PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    base_path = filedialog.askdirectory(title="Selecciona la carpeta del proyecto")

    if not base_path:
        print("No se seleccionó ninguna carpeta. Saliendo...")
        exit()

    print("Selecciona el tipo de archivo a analizar:")
    print("1. Archivos Python (.py)")
    print("2. Archivos HTML (.html)")
    print("3. Archivos CSS (.css)")
    opcion = input("Ingresa el número de tu elección: ").strip()

    extension = { "1": ".py", "2": ".html", "3": ".css" }.get(opcion)
    if not extension:
        print("Opción inválida. Saliendo...")
        exit()

    analizador = AnalizadorProyecto(base_path, extension)
    analizador.analizar_archivos()
    analizador.generar_html()
    analizador.generar_pdf()