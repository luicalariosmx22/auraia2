print("🚀 VERSIÓN CORREGIDA DEL APP.PY - SÍ ESTOY ACTUALIZADO 🚀")

from gevent import monkey

monkey.patch_all()  # ✅ Apply gevent monkey patching

import os
import uuid
import logging
from flask import Flask, session, redirect, url_for, request, jsonify
from flask_session import Session
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from clientes.aura.utils.debug_rutas import generar_html_rutas
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.extensions.socketio_instance import socketio
from werkzeug.serving import WSGIRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz  # Para manejar zonas horarias
from clientes.aura.tasks.meta_ads_reporter import enviar_reporte_semanal

print("📥 Importando módulo Ads...")
from clientes.aura.modules.ads import ads_bp  # ✅ Updated import

print("✅ Módulo Ads importado correctamente.")

# 👇 Import actualizado
from clientes.aura.routes.panel_cliente_ads import panel_cliente_ads_bp

# ✅ Nueva import del archivo renombrado
from clientes.aura.utils.blueprint_utils_v2 import registrar_blueprints_login

from clientes.aura.registro.registro_base import registrar_blueprints_base
from clientes.aura.registro.registro_admin import registrar_blueprints_admin
from clientes.aura.registro.registro_debug import registrar_blueprints_debug
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.webhook import webhook_bp
from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
from clientes.aura.routes.etiquetas import etiquetas_bp
from clientes.aura.routes.panel_cliente import panel_cliente_bp
from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
from clientes.aura.routes.admin_verificador_rutas import admin_verificador_bp
from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
from clientes.aura.routes.admin_noras import admin_noras_bp  # 👈 Added import
from clientes.aura.routes.admin_nora import admin_nora_bp
from clientes.aura.routes.cliente_nora import cliente_nora_bp
from clientes.aura.routes.cobranza import cobranza_bp
from clientes.aura.routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
from clientes.aura.registro.registro_invitado import registrar_blueprints_invitado

# ⬇️ IMPORTAMOS la instancia global de socketio
from clientes.aura.extensiones import socketio

# ✅ Asegurar este import
from clientes.aura.registro.registro_dinamico import registrar_blueprints_por_nora

from gunicorn.app.base import BaseApplication
from typing import Dict, Any

import flask
import gunicorn

try:
    # Método moderno para obtener la versión de Werkzeug
    from werkzeug import __version__ as werkzeug_version
except ImportError:
    try:
        # Fallback para versiones más antiguas o si Werkzeug no está accesible
        import werkzeug
        werkzeug_version = werkzeug.__version__
    except (ImportError, AttributeError):
        try:
            # Otro fallback usando pkg_resources
            import pkg_resources
            werkzeug_version = pkg_resources.get_distribution("werkzeug").version
        except Exception:
            werkzeug_version = "No se pudo determinar la versión de Werkzeug"

print(f"Flask version: {flask.__version__}")
print(f"Gunicorn version: {gunicorn.__version__}")
print(f"Werkzeug version: {werkzeug_version}")

class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        return ' 200 -' not in record.getMessage()

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(WerkzeugFilter())

socketio_log = logging.getLogger('socketio_polling')
socketio_log.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/socketio_polling.log", maxBytes=100000, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
socketio_log.addHandler(handler)

load_dotenv()

logging.getLogger("twilio.http_client").setLevel(logging.WARNING)

app = Flask(
    __name__,
    template_folder='clientes/aura/templates',
    static_folder='clientes/aura/static'
)

app.session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
app.secret_key = os.environ.get("SECRET_KEY", "clave-secreta-por-defecto")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ⬇️ Inicializamos socketio usando la instancia global
socketio.init_app(app)

if not app.debug:
    file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# ✅ Scheduler para reportes automáticos
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Hermosillo'))

scheduler.add_job(
    func=enviar_reporte_semanal,
    trigger=CronTrigger(
        day_of_week='mon',  # 'mon' para lunes
        hour=10,            # Para las 10 AM
        minute=0,
        timezone='America/Hermosillo'  # Zona horaria específica
    ),
    id='job_enviar_reporte_semanal',  # ID único para el trabajo
    name='Reporte Semanal Meta Ads Aura',
    replace_existing=True  # Reemplaza el trabajo si ya existe con este ID
)

scheduler.start()

# 👇 Para registrar los blueprints sin duplicarlos:
def safe_register_blueprint(app, blueprint, **kwargs):
    """
    Registra un blueprint de forma segura, evitando duplicados.
    """
    unique_name = kwargs.pop("name", blueprint.name)
    if unique_name not in app.blueprints:
        app.register_blueprint(blueprint, name=unique_name, **kwargs)
        print(f"✅ Blueprint '{unique_name}' registrado")
    else:
        print(f"⚠️ Blueprint ya estaba registrado: {unique_name}")

# ========= REGISTRO DE BLUEPRINTS =========

# ✅ Registro del login con función segura
registrar_blueprints_login(app, safe_register_blueprint)

# Blueprints globales
registrar_blueprints_base(app, safe_register_blueprint)
registrar_blueprints_admin(app, safe_register_blueprint)
registrar_blueprints_debug(app, safe_register_blueprint)
registrar_blueprints_invitado(app, safe_register_blueprint)

blueprints_estaticos = [
    (admin_verificador_bp, None),
    (panel_chat_bp, None),
    (admin_nora_dashboard_bp, None),
    (webhook_bp, None),
    (etiquetas_bp, "/panel_cliente_etiquetas"),
    (panel_cliente_bp, "/panel_cliente"),
    (panel_cliente_contactos_bp, "/panel_cliente/contactos"),
    (panel_cliente_envios_bp, "/panel_cliente/envios"),
    (admin_nora_bp, "/admin/nora"),
    (cliente_nora_bp, "/panel_cliente"),
    (panel_cliente_conocimiento_bp, "/panel_cliente/conocimiento"),
    (panel_cliente_ads_bp, f"/panel_cliente/{{nombre_nora}}/ads"),  # ✅ Added blueprint registration
]

print("🔄 Registrando blueprints estáticos...")
for blueprint, prefix in blueprints_estaticos:
    safe_register_blueprint(app, blueprint, url_prefix=prefix)

app.register_blueprint(cobranza_bp, url_prefix="/api")

# Blueprints dinámicos por Nora
try:
    response = supabase.table("configuracion_bot").select("nombre_nora").execute()
    nombre_noras = [n["nombre_nora"] for n in response.data] if response.data else []

    for nombre in nombre_noras:
        registrar_blueprints_por_nora(app, nombre_nora=nombre, safe_register_blueprint=safe_register_blueprint)
    registrar_blueprints_por_nora(app, nombre_nora="aura", safe_register_blueprint=safe_register_blueprint)  # Cambia "aura" por cada Nora real si necesario
except Exception as e:
    app.logger.error(f"Error al registrar Noras dinámicas: {e}")

def validar_o_generar_uuid(valor):
    try:
        return str(uuid.UUID(valor))
    except (ValueError, TypeError):
        return str(uuid.uuid4())

def registrar_rutas_en_supabase():
    rutas = []
    for rule in app.url_map.iter_rules():
        rutas.append({
            "id": validar_o_generar_uuid(""),
            "ruta": rule.rule,
            "blueprint": rule.endpoint.split(".")[0] if "." in rule.endpoint else "default",
            "metodo": ", ".join(rule.methods - {"HEAD", "OPTIONS"}),
            "registrado_en": datetime.now().isoformat()
        })
    try:
        response = supabase.table("rutas_registradas").insert(rutas).execute()
    except Exception as e:
        app.logger.error(f"Error al registrar rutas en Supabase: {str(e)}")

app.logger.info(f"📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")

@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard.dashboard_admin"))
    else:
        return redirect(url_for("panel_cliente.configuracion_cliente", nombre_nora=session.get("nombre_nora", "aura")))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login_google"))

@app.route('/debug_info', methods=['GET'])
def debug_info():
    return jsonify({
        "rutas_registradas": [rule.rule for rule in app.url_map.iter_rules()],
        "estado": "OK",
    })

@app.before_request
def log_polling_requests():
    if request.path.startswith('/socket.io') and request.args.get('transport') == 'polling':
        socketio_log.info(f"{request.remote_addr} - {request.method} {request.full_path}")

class GunicornApplication(BaseApplication):
    """
    Wrapper para lanzar Gunicorn desde código.
    """
    def __init__(self, app_object, options: Dict[str, Any] | None = None):
        # Usamos app_object como nombre del parámetro para evitar confusión con self.app de BaseApplication
        self.options: Dict[str, Any] = options or {}
        self.application_obj = app_object  # Guardamos el objeto Flask aquí
        # Logueamos antes de llamar al super
        app.logger.info("[GunicornApplication] __init__: Inicializando. Opciones: %s", self.options)
        try:
            super().__init__()
            app.logger.info("[GunicornApplication] __init__: super().__init__() completado.")
        except Exception as e:
            app.logger.error("[GunicornApplication] __init__: ERROR durante super().__init__(): %s", str(e), exc_info=True)
            raise

    def load_config(self):
        app.logger.info("[GunicornApplication] load_config: Iniciando carga de configuración.")
        try:
            # 1. Crea el objeto de configuración desde self.cfg_cls.
            self.cfg = self.cfg_cls()
            app.logger.info("[GunicornApplication] load_config: self.cfg inicializado desde self.cfg_cls().")

            # 2. Aplica las opciones programáticas al objeto cfg.
            app.logger.info("[GunicornApplication] load_config: Aplicando opciones programáticas al cfg.")
            for key, value in self.options.items():
                setting_name = key.lower()
                # Verifica si la configuración existe en el objeto cfg de Gunicorn.
                if setting_name in self.cfg.settings:
                    self.cfg.set(setting_name, value)
                    app.logger.debug("[GunicornApplication] load_config: Opción aplicada: %s = %s", setting_name, value)
                else:
                    app.logger.warning("[GunicornApplication] load_config: Opción de Gunicorn desconocida o no es un 'setting': '%s'", key)
            
            app.logger.info("[GunicornApplication] load_config: Configuración cargada exitosamente.")
        except Exception as e:
            app.logger.error("[GunicornApplication] load_config: ERROR durante load_config: %s", str(e), exc_info=True)
            # Relanza la excepción para indicar que falló la carga de configuración.
            raise

    def load(self):
        app.logger.info("[GunicornApplication] load: Cargando la aplicación Flask.")
        # Devuelve el objeto Flask que guardamos
        return self.application_obj

# Configuración de Gunicorn con gevent
options = {
    'bind': '0.0.0.0:' + str(os.environ.get('PORT', 5000)),
    'workers': int(os.environ.get('WEB_CONCURRENCY', 4)),  # Configurable por variable de entorno
    'worker_class': 'gevent',
    'timeout': 120,  # Ejemplo: Aumentar el timeout si tienes operaciones largas
}

# ──────────────────────────────────────────
# Lanzar la aplicación con Gunicorn
# ──────────────────────────────────────────
if __name__ == "__main__":
    app.logger.info("============================================================")
    app.logger.info("INICIANDO BLOQUE if __name__ == '__main__':")
    app.logger.info("Intentando iniciar Gunicorn programáticamente...")
    app.logger.info("Opciones de Gunicorn a usar: %s", options)

    try:
        # Pasamos 'app' (tu instancia de Flask) y 'options' a GunicornApplication
        gunicorn_app = GunicornApplication(app, options)
        app.logger.info("Instancia de GunicornApplication creada.")
        
        app.logger.info("Llamando a gunicorn_app.run()...")
        gunicorn_app.run()  # Esto bloqueará si Gunicorn se inicia correctamente
        
        # Si gunicorn_app.run() retorna, significa que Gunicorn se detuvo
        app.logger.info("gunicorn_app.run() ha finalizado.")

    except SystemExit as se:
        app.logger.error("SystemExit capturado en __main__: Código de salida %s. Gunicorn probablemente falló al iniciar.", se.code, exc_info=True)
        if se.code != 0:
            raise  # Relanza la excepción si fue una salida con error
    except Exception as e:
        app.logger.error("ERROR FATAL al intentar iniciar o ejecutar Gunicorn en __main__: %s", str(e), exc_info=True)
        raise
    finally:
        app.logger.info("Bloque if __name__ == '__main__' finalizado.")
        app.logger.info("============================================================")