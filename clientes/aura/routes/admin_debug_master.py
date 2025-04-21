import os
import openai
import re
from flask import Blueprint, render_template, request, current_app
from dotenv import load_dotenv
from clientes.aura.routes import admin_debug_rutas
from clientes.aura.debug import debug_supabase
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.routes.debug_verificar import verificar_sistema
from clientes.aura.utils.verificador_rutas import RutaChecker

admin_debug_master_bp = Blueprint("admin_debug_master", __name__)
my_blueprint = Blueprint('my_blueprint', __name__)

@my_blueprint.route('/ruta-no-definida')
def ruta_no_definida():
    return "¡Hola, esta es la ruta no definida!"

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extraer_rutas_desde_templates(templates_path):
    """
    Extrae rutas desde los archivos de plantilla HTML.

    Args:
        templates_path (str): Ruta al directorio de plantillas.

    Returns:
        list: Lista de diccionarios con detalles de las rutas extraídas.
    """
    rutas = []
    try:
        for root, _, files in os.walk(templates_path):
            for file in files:
                if file.endswith(".html"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        contenido = f.read()
                        # Busca rutas en los atributos href
                        matches = re.findall(r'href="([^"]+)"', contenido)
                        for match in matches:
                            rutas.append({"archivo": file, "ruta": match})
    except Exception as e:
        print(f"❌ Error al extraer rutas desde plantillas: {str(e)}")
    return rutas

def extraer_rutas_flask(routes_path):
    """
    Extrae rutas registradas en Flask desde un directorio de rutas.

    Args:
        routes_path (str): Ruta al directorio de rutas.

    Returns:
        list: Lista de diccionarios con detalles de las rutas registradas.
    """
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

def generar_controladores_para_rutas_no_definidas(rutas_no_definidas):
    """
    Genera controladores básicos para las rutas no definidas.

    Args:
        rutas_no_definidas (list): Lista de rutas no definidas.
    """
    for ruta in rutas_no_definidas:
        print(f"Creando controlador para la ruta: {ruta['ruta']}")
        # Limpia el nombre del archivo
        nombre_archivo = re.sub(r'[^a-zA-Z0-9_]', '_', ruta['ruta'].strip('/'))
        with open(f"clientes/aura/routes/{nombre_archivo}.py", "w", encoding="utf-8") as f:
            f.write(f"""
from flask import Blueprint

generated_blueprint = Blueprint('generated_blueprint', __name__)

@generated_blueprint.route('{ruta['ruta']}')
def {nombre_archivo}():
    return "¡Esta es una ruta generada automáticamente para {ruta['ruta']}!"
""")

@admin_debug_master_bp.route("/admin/debug/master", methods=["GET", "POST"])
def debug_master():
    if request.method not in ["GET", "POST"]:
        return "❌ Método HTTP no permitido", 405

    try:
        # Inicialización de variables
        resultado_verificacion = ""

        # 1️⃣ Verificar Rutas
        try:
            # Extraer rutas desde las plantillas HTML y Flask
            checker = RutaChecker()
            checker.analizar_rutas("clientes/aura")
            resultado_verificacion = checker.generar_html()
        except Exception as e:
            resultado_verificacion = f"❌ Error al verificar rutas: {str(e)}"

        # Renderizar resultados en la plantilla
        return render_template(
            "admin_debug_master.html",
            resultado_verificacion=resultado_verificacion,
        )
    except Exception as e:
        # Registrar errores críticos
        print(f"❌ Error crítico en debug_master: {str(e)}")
        return render_template(
            "error.html",
            mensaje="❌ Error crítico en el servidor. Por favor, contacta al administrador.",
            detalle=str(e),
        )