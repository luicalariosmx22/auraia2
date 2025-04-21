import os
import openai
import re
import logging
from flask import Blueprint, render_template, request, current_app, jsonify
from dotenv import load_dotenv
from clientes.aura.routes import admin_debug_rutas
from clientes.aura.debug import debug_supabase
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.routes.debug_verificar import verificar_sistema
from clientes.aura.utils.verificador_rutas import RutaChecker
from clientes.aura.utils.supabase import supabase

# Configurar logs
logging.basicConfig(level=logging.DEBUG)

admin_debug_master_bp = Blueprint("admin_debug_master", __name__)
my_blueprint = Blueprint('my_blueprint', __name__)

@my_blueprint.route('/ruta-no-definida')
def ruta_no_definida():
    return "¡Hola, esta es la ruta no definida!"

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    current_app.logger.warning("⚠️ La clave de API de OpenAI no está configurada.")

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

def registrar_rutas_generadas(app):
    rutas_generadas_path = "clientes/aura/routes"
    for root, _, files in os.walk(rutas_generadas_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_name = f"clientes.aura.routes.{file[:-3]}"
                module = __import__(module_name, fromlist=["generated_blueprint"])
                if hasattr(module, "generated_blueprint"):
                    app.register_blueprint(module.generated_blueprint)

def verificar_rutas():
    try:
        checker = RutaChecker()
        checker.analizar_rutas("clientes/aura")
        return checker.generar_html()
    except FileNotFoundError as e:
        return f"❌ Error: No se encontró el archivo o directorio: {str(e)}"
    except Exception as e:
        return f"❌ Error inesperado al verificar rutas: {str(e)}"

def validar_blueprints(app, routes_path):
    """
    Valida los blueprints registrados en la aplicación con los archivos en el directorio de rutas.

    Args:
        app (Flask): La instancia de la aplicación Flask.
        routes_path (str): Ruta al directorio de rutas.

    Returns:
        dict: Resultados de la validación.
    """
    registrados = set(app.blueprints.keys())
    encontrados = set()

    # Buscar blueprints en los archivos de rutas
    for root, _, files in os.walk(routes_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    contenido = f.read()
                    matches = re.findall(r"Blueprint\(['\"]([^'\"]+)['\"]", contenido)
                    encontrados.update(matches)

    # Comparar los blueprints registrados con los encontrados
    faltantes = encontrados - registrados
    extras = registrados - encontrados

    return {
        "registrados": list(registrados),
        "encontrados": list(encontrados),
        "faltantes": list(faltantes),
        "extras": list(extras),
    }

def validar_rutas_dinamicas(robot_nombre):
    """
    Valida las rutas dinámicas relacionadas con un robot específico.

    Args:
        robot_nombre (str): Nombre del robot.

    Returns:
        dict: Resultados de la validación.
    """
    rutas = []
    try:
        # Obtener las rutas dinámicas relacionadas con el robot
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", robot_nombre).execute()
        if not response.data:
            return {"error": f"No se encontró el robot con nombre: {robot_nombre}"}

        robot_config = response.data[0]
        modulos = robot_config.get("modulos", [])

        # Generar rutas dinámicas basadas en los módulos
        for modulo in modulos:
            rutas.append(f"/{robot_nombre}/{modulo}")

        # Validar si las rutas están registradas en Flask
        rutas_registradas = [rule.rule for rule in current_app.url_map.iter_rules()]
        rutas_faltantes = [ruta for ruta in rutas if ruta not in rutas_registradas]

        return {
            "rutas_generadas": rutas,
            "rutas_faltantes": rutas_faltantes,
        }
    except Exception as e:
        return {"error": str(e)}

@admin_debug_master_bp.route("/master", methods=["GET", "POST"])
def debug_master():
    try:
        checker = RutaChecker()
        checker.analizar_rutas("clientes/aura")
        rutas_no_definidas = checker.rutas_no_definidas

        return render_template(
            "admin_debug_master.html",
            resultado_verificacion=checker.generar_html(),
            rutas_no_definidas=rutas_no_definidas,
        )
    except Exception as e:
        current_app.logger.error(f"❌ Error crítico en debug_master: {str(e)}")
        return render_template(
            "error.html",
            mensaje="❌ Error crítico en el servidor. Por favor, contacta al administrador.",
            detalle=str(e),
        )

@admin_debug_master_bp.route("/admin/debug/blueprints", methods=["GET"])
def debug_blueprints():
    """
    Endpoint para validar los blueprints registrados en la aplicación.
    """
    resultados = validar_blueprints(current_app, "clientes/aura/routes")
    return jsonify(resultados)

@admin_debug_master_bp.route("/admin/debug/rutas_dinamicas/<robot_nombre>", methods=["GET"])
def debug_rutas_dinamicas(robot_nombre):
    """
    Endpoint para validar rutas dinámicas relacionadas con un robot específico.
    """
    resultados = validar_rutas_dinamicas(robot_nombre)
    return jsonify(resultados)

@admin_debug_master_bp.route("/admin/debug/probar_rutas_dinamicas/<robot_nombre>", methods=["GET"])
def probar_rutas_dinamicas(robot_nombre):
    """
    Prueba rutas dinámicas relacionadas con un robot específico.
    """
    try:
        # Obtener datos del robot desde Supabase
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", robot_nombre).execute()
        if not response.data:
            return jsonify({"error": f"No se encontró el robot con nombre: {robot_nombre}"})

        robot_config = response.data[0]
        modulos = robot_config.get("modulos", [])

        # Generar rutas dinámicas
        rutas_dinamicas = [f"/panel_cliente/{robot_nombre}/{modulo}" for modulo in modulos]

        # Validar si las rutas están registradas
        rutas_registradas = [rule.rule for rule in current_app.url_map.iter_rules()]
        rutas_faltantes = [ruta for ruta in rutas_dinamicas if ruta not in rutas_registradas]

        # Probar accesibilidad de las rutas dinámicas
        rutas_accesibles = {}
        for ruta in rutas_dinamicas:
            try:
                with current_app.test_client() as client:
                    response = client.get(ruta)
                    rutas_accesibles[ruta] = {
                        "accesible": response.status_code == 200,
                        "status_code": response.status_code,
                        "error": None
                    }
            except Exception as e:
                rutas_accesibles[ruta] = {
                    "accesible": False,
                    "status_code": None,
                    "error": str(e)
                }

        return jsonify({
            "rutas_dinamicas": rutas_dinamicas,
            "rutas_faltantes": rutas_faltantes,
            "rutas_accesibles": rutas_accesibles,
        })
    except Exception as e:
        current_app.logger.error(f"Error al probar rutas dinámicas: {str(e)}")
        return jsonify({"error": str(e)})

@admin_debug_master_bp.route("/admin/debug/rutas", methods=["GET"])
def debug_rutas():
    """
    Devuelve todas las rutas registradas en la aplicación Flask.
    """
    rutas_registradas = []
    for rule in current_app.url_map.iter_rules():
        rutas_registradas.append({
            "ruta": rule.rule,
            "endpoint": rule.endpoint,
            "metodos": list(rule.methods - {"HEAD", "OPTIONS"})  # Excluir métodos no relevantes
        })

    return jsonify({"rutas_registradas": rutas_registradas})

@admin_debug_master_bp.route("/admin/debug/rutas_no_registradas", methods=["GET"])
def rutas_no_registradas():
    """
    Detecta rutas esperadas que no están registradas en Flask.
    """
    rutas_esperadas = [
        "/panel_cliente/<cliente>/<nombre_nora>",
        "/admin/noras",
        "/admin/debug/master",
        # Agrega aquí más rutas esperadas
    ]

    rutas_registradas = [rule.rule for rule in current_app.url_map.iter_rules()]
    rutas_faltantes = [ruta for ruta in rutas_esperadas if ruta not in rutas_registradas]

    return jsonify({"rutas_faltantes": rutas_faltantes})

@admin_debug_master_bp.route("/admin/debug/logs", methods=["GET"])
def mostrar_logs():
    """
    Muestra los logs generados por la aplicación.
    """
    try:
        with open("debug.log", "r") as log_file:
            logs = log_file.readlines()
        return jsonify({"logs": logs})
    except FileNotFoundError:
        return jsonify({"error": "No se encontró el archivo de logs."})