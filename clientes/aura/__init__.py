# clientes/aura/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session as flask_session, redirect, url_for, request, jsonify
from flask_session import Session
from dotenv import load_dotenv

# Tus módulos modulares
from .app_config import Config
from .extensiones import socketio, session_ext, scheduler # ¡Corregido a 'extensiones.py'!

# Para APScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks.meta_ads_reporter import enviar_reporte_semanal

# Para Blueprints y registro
# Importa tus funciones de registro de blueprints
from .registro.registro_login import registrar_blueprints_login # Asumiendo que existe y tiene esta función
from .registro.registro_base import registrar_blueprints_base
from .registro.registro_admin import registrar_blueprints_admin
from .registro.registro_debug import registrar_blueprints_debug
from .registro.registro_invitado import registrar_blueprints_invitado
from .registro.registro_dinamico import registrar_blueprints_por_nora # Para los dinámicos

# Importa los objetos Blueprint (_bp) que se usan en la lista 'blueprints_estaticos'
# o que se registran directamente.
from .routes.admin_verificador_rutas import admin_verificador_bp # Lo tenías en app.py original
from .routes.panel_chat import panel_chat_bp
from .routes.webhook import webhook_bp
from .routes.admin_nora_dashboard import admin_nora_dashboard_bp
from .routes.etiquetas import etiquetas_bp
from .routes.panel_cliente_contactos import panel_cliente_contactos_bp
from .routes.panel_cliente_envios import panel_cliente_envios_bp
from .routes.admin_nora import admin_nora_bp
from .routes.admin_noras import admin_noras_bp # Lo tenías en app.py original
from .routes.cliente_nora import cliente_nora_bp
from .routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
from .routes.panel_cliente_ads import panel_cliente_ads_bp
from .routes.cobranza import cobranza_bp
# from .modules.ads import ads_bp # ¿Aún necesitas este o fue reemplazado por panel_cliente_ads_bp?

# Para la lógica de blueprints dinámicos
from .utils.supabase_client import supabase
import uuid # Para validar_o_generar_uuid
from datetime import datetime # Para registrar_rutas_en_supabase

# --- Clases y Funciones de Utilidad (Definidas aquí o importadas si las mueves a utils) ---
class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        if 'socket.io' in record.getMessage() and 'polling' in record.getMessage():
            return False
        return ' 200 -' not in record.getMessage()

def safe_register_blueprint(app, blueprint, **kwargs):
    unique_name = kwargs.pop("name", blueprint.name)
    if unique_name not in app.blueprints:
        app.register_blueprint(blueprint, name=unique_name, **kwargs)
        print(f"✅ Blueprint '{unique_name}' registrado con nombre '{unique_name}' y prefijo '{kwargs.get('url_prefix', '')}'")
    else:
        print(f"⚠️ Blueprint '{unique_name}' ya estaba registrado.")

# Funciones que estaban en tu app.py original (podrían ir a utils si prefieres)
def validar_o_generar_uuid(valor):
    try:
        return str(uuid.UUID(str(valor))) # Asegurar que valor es string
    except (ValueError, TypeError, AttributeError): # AttributeError por si valor es None
        return str(uuid.uuid4())

def registrar_rutas_en_supabase_db(app_instance): # Renombrado para evitar confusión con tu archivo registrar_rutas.py
    rutas = []
    for rule in app_instance.url_map.iter_rules():
        # Usar el nombre del blueprint si está disponible, sino 'default' o el nombre del endpoint
        blueprint_name = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'default_route'
        # Si el endpoint no tiene blueprint, podrías querer loguearlo o manejarlo diferente
        if blueprint_name == rule.endpoint and blueprint_name not in app_instance.blueprints:
            blueprint_name = 'app_level_route' # O alguna otra designación

        rutas.append({
            "id": validar_o_generar_uuid(None), # Pasar None para generar siempre nuevo UUID
            "ruta": rule.rule,
            "blueprint": blueprint_name,
            "metodo": ", ".join(sorted(list(rule.methods - {"HEAD", "OPTIONS"}))),
            "registrado_en": datetime.now().isoformat()
        })
    if rutas: # Solo intentar insertar si hay rutas
        try:
            # Asumo que 'supabase' es tu cliente de Supabase importado
            response = supabase.table("rutas_registradas").upsert(rutas, on_conflict='ruta,metodo').execute() # Usar upsert
            app_instance.logger.info(f"Rutas (re)insertadas/actualizadas en Supabase. Respuesta: {response}")
        except Exception as e:
            app_instance.logger.error(f"Error al (re)insertar/actualizar rutas en Supabase: {str(e)}", exc_info=True)


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    load_dotenv()

    # --- INICIO DE CAMBIOS PARA DEPURACIÓN ---
    print(f"DEBUG: Objeto config_class ANTES de from_object: {config_class}")
    if hasattr(config_class, 'SESSION_COOKIE_NAME'):
        print(f"DEBUG: config_class TIENE SESSION_COOKIE_NAME: {getattr(config_class, 'SESSION_COOKIE_NAME')}")
    else:
        print("DEBUG: config_class NO TIENE SESSION_COOKIE_NAME")

    app.config.from_object(config_class)

    # Asegurarse de que SESSION_COOKIE_NAME esté configurado
    if 'SESSION_COOKIE_NAME' not in app.config:
        app.config['SESSION_COOKIE_NAME'] = 'aura_session'

    print(f"DEBUG: SESSION_COOKIE_NAME configurado como: {app.config['SESSION_COOKIE_NAME']}")
    print(f"DEBUG: SECRET_KEY DESPUÉS de from_object: {app.config.get('SECRET_KEY')}")
    print(f"DEBUG: SESSION_TYPE DESPUÉS de from_object: {app.config.get('SESSION_TYPE')}")
    # --- FIN DE CAMBIOS PARA DEPURACIÓN ---

    print("🚀 Aplicación Flask creada y configuración inicial cargada por la factory.")

    # Inicializar extensiones
    Session(app)  # Activa correctamente Flask-Session con SESSION_TYPE = filesystem
    socketio.init_app(app)
    print("Extensiones Flask-Session y Flask-SocketIO inicializadas.")

    # Configurar Logging
    # (Tu lógica de logging que ya tenías aquí, incluyendo WerkzeugFilter, error.log, socketio_polling.log, Twilio)
    if not app.debug:
        try:
            if not os.path.exists('logs') and os.name != 'nt':
                try: os.makedirs('logs')
                except OSError as e: print(f"No se pudo crear carpeta 'logs': {e}")
            error_file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
            error_file_handler.setLevel(logging.ERROR)
            error_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            error_file_handler.setFormatter(error_formatter)
            app.logger.addHandler(error_file_handler)
            print("Handler de logging para errores de app configurado (error.log).")
        except Exception as e:
            print(f"No se pudo configurar el archivo de log para errores de app: {e}")

        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.addFilter(WerkzeugFilter())
        print("Filtro de logging para Werkzeug añadido.")

        socketio_polling_log = logging.getLogger('socketio_polling_custom')
        socketio_polling_log.setLevel(logging.INFO)
        try:
            socketio_polling_file_handler = RotatingFileHandler("logs/socketio_polling.log", maxBytes=100000, backupCount=3)
            socketio_polling_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            socketio_polling_log.addHandler(socketio_polling_file_handler)
            print("Handler de logging para socketio_polling configurado (logs/socketio_polling.log).")
        except Exception as e:
            print(f"No se pudo configurar el archivo de log para socketio_polling: {e}")

    logging.getLogger("twilio.http_client").setLevel(logging.WARNING)
    print("Nivel de logging para twilio.http_client establecido a WARNING.")

    # Registrar Tareas APScheduler
    if not scheduler.running:
        scheduler.add_job(
            func=enviar_reporte_semanal,
            trigger=CronTrigger(day_of_week='mon', hour=10, minute=0, timezone='America/Hermosillo'),
            id='job_enviar_reporte_semanal',
            name='Reporte Semanal Meta Ads Aura',
            replace_existing=True
        )
        try:
            scheduler.start()
            print("APScheduler iniciado y trabajo 'enviar_reporte_semanal' añadido.")
        except Exception as e:
            print(f"Error al iniciar APScheduler o añadir job: {e}")
    else:
        print("APScheduler ya estaba corriendo.")

    # --- Registrar Blueprints ---
    print("Iniciando registro de Blueprints...")
    registrar_blueprints_login(app, safe_register_blueprint)
    registrar_blueprints_base(app, safe_register_blueprint)
    registrar_blueprints_admin(app, safe_register_blueprint)
    registrar_blueprints_debug(app, safe_register_blueprint)
    registrar_blueprints_invitado(app, safe_register_blueprint)
    print("Registro de Blueprints completado.")

    # Blueprints dinámicos
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora").execute()
        nombre_noras = [n["nombre_nora"] for n in response.data] if response.data else []
        print(f"Nora(s) encontradas en Supabase para registro dinámico: {nombre_noras}")
        for nombre in nombre_noras:
            registrar_blueprints_por_nora(app, nombre_nora=nombre, safe_register_blueprint=safe_register_blueprint)
        # Considera si necesitas registrar 'aura' explícitamente aquí o si ya viene de Supabase
        # registrar_blueprints_por_nora(app, nombre_nora="aura", safe_register_blueprint=safe_register_blueprint)
    except Exception as e:
        print(f"Error al registrar Noras dinámicas: {e}")
    print("Registro de Blueprints completado.")

    # --- Rutas de Nivel de Aplicación ---
    print("Definiendo rutas de nivel de aplicación...")
    @app.route("/")
    def home():
        if "user" not in flask_session:
            return redirect(url_for("login.login_google"))  # Updated blueprint name
        if flask_session.get("is_admin"):
            return redirect(url_for("admin_nora_dashboard_bp.dashboard_admin"))
        else:
            return redirect(url_for("panel_cliente_bp.configuracion_cliente", nombre_nora=flask_session.get("nombre_nora", "aura")))

    @app.route("/logout")
    def logout():
        flask_session.clear()
        return redirect(url_for("login.login_google"))  # Updated blueprint name

    @app.route('/debug_info', methods=['GET'])
    def debug_info():
        return jsonify({
            "blueprints_registrados": list(app.blueprints.keys()),  # Added registered blueprints
            "rutas_registradas": [str(rule) for rule in app.url_map.iter_rules()],
            "estado": "OK",
        })

    @app.route('/healthz')
    def health_check():
        return "OK", 200
    print("Rutas de nivel de aplicación definidas.")

    # --- before_request handler ---
    print("Definiendo handler before_request...")
    @app.before_request
    def log_polling_requests():
        if request.path.startswith('/socket.io') and request.args.get('transport') == 'polling':
            # Obtener el logger configurado para socketio polling
            socketio_polling_logger = logging.getLogger('socketio_polling_custom')
            socketio_polling_logger.info(f"{request.remote_addr} - {request.method} {request.full_path}")
    print("Handler before_request definido.")

    print(f"📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")
    print("Función create_app completada.")
    return app