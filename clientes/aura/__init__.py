def initialize_app(app):
    """
    Inicializa blueprints, tareas y componentes adicionales en la app Flask.
    """
    try:
        from .registro.registro_login import registrar_blueprints_login
        from .registro.registro_base import registrar_blueprints_base
        from .registro.registro_admin import registrar_blueprints_admin
        from .registro.registro_debug import registrar_blueprints_debug
        from .registro.registro_invitado import registrar_blueprints_invitado
        from .registro.registro_dinamico import registrar_blueprints_por_nora

        registrar_blueprints_login(app, safe_register_blueprint)
        registrar_blueprints_base(app, safe_register_blueprint)
        registrar_blueprints_admin(app, safe_register_blueprint)
        registrar_blueprints_debug(app, safe_register_blueprint)
        registrar_blueprints_invitado(app, safe_register_blueprint)

        # Blueprints de tareas
        from clientes.aura.routes.panel_cliente_tareas import register_tareas_blueprints
        register_tareas_blueprints(app)

        # Registrar Blueprint de Meta Ads
        from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_meta import webhooks_meta_bp
        from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_routes import automatizacion_routes_bp
        safe_register_blueprint(app, panel_cliente_meta_ads_bp)
        safe_register_blueprint(app, webhooks_meta_bp)
        safe_register_blueprint(app, automatizacion_routes_bp)

        # Blueprints específicos adicionales
        from clientes.aura.routes.panel_team.vista_panel_team import panel_team_bp
        from clientes.aura.routes.panel_cliente_pagos.vista_presupuestos import panel_cliente_pagos_presupuestos_bp
        from clientes.aura.routes.panel_cliente_pagos.vista_presupuesto_nuevo import panel_cliente_pagos_presupuesto_nuevo_bp
        from clientes.aura.routes.panel_cliente_tareas.tareas_completadas import panel_tareas_completadas_bp
        from clientes.aura.routes.cliente_nora import cliente_nora_bp
        safe_register_blueprint(app, panel_team_bp, url_prefix="/panel_team")
        safe_register_blueprint(app, panel_cliente_pagos_presupuestos_bp, url_prefix="/panel_cliente")
        safe_register_blueprint(app, panel_cliente_pagos_presupuesto_nuevo_bp, url_prefix="/panel_cliente")
        safe_register_blueprint(app, panel_tareas_completadas_bp, url_prefix="/panel_cliente")
        safe_register_blueprint(app, cliente_nora_bp, url_prefix="")

        # Blueprints dinámicos
        from .utils.supabase_client import supabase
        response = supabase.table("configuracion_bot").select("nombre_nora").execute()
        nombre_noras = [n["nombre_nora"] for n in response.data] if response.data else []
        print(f"Nora(s) encontradas en Supabase para registro dinámico: {nombre_noras}")
        for nombre in nombre_noras:
            registrar_blueprints_por_nora(app, nombre_nora=nombre, safe_register_blueprint=safe_register_blueprint)

        # Inicializar tareas programadas
        from flask_apscheduler import APScheduler
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        inicializar_cron_jobs_seguros(scheduler)
        print("✅ Scheduler inicializado correctamente")

        app.config['INITIALIZATION_COMPLETE'] = True
        print("✅ Inicialización secuencial completada")
    except Exception as e:
        app.logger.exception(f"❌ Error en inicialización: {str(e)}")
        if 'INITIALIZATION_ERRORS' in app.config:
            app.config['INITIALIZATION_ERRORS'].append(f"Error general: {str(e)}")

# clientes/aura/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session, redirect, url_for, request, jsonify
from flask_session import Session
from dotenv import load_dotenv
from datetime import timedelta, datetime
import threading
import time
import werkzeug
from werkzeug.http import dump_cookie as original_dump_cookie

# Tus módulos modulares
from .app_config import Config
from .extensiones import socketio, session_ext, scheduler

# Para APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

# --- Clases y Funciones de Utilidad ---
class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        if 'socket.io' in record.getMessage() and 'polling' in record.getMessage():
            return False
        return ' 200 -' not in record.getMessage()

def safe_register_blueprint(app, blueprint, **kwargs):
    """Registra un blueprint de forma segura, evitando duplicados"""
    unique_name = kwargs.pop("name", blueprint.name)
    if unique_name not in app.blueprints:
        app.register_blueprint(blueprint, name=unique_name, **kwargs)
        print(f"✅ Blueprint '{unique_name}' registrado con nombre '{unique_name}' y prefijo '{kwargs.get('url_prefix', '')}'")
    else:
        print(f"⚠️ Blueprint '{unique_name}' ya estaba registrado.")

def validar_o_generar_uuid(valor):
    """Valida un UUID o genera uno nuevo si es inválido"""
    import uuid
    try:
        return str(uuid.UUID(str(valor)))
    except (ValueError, TypeError, AttributeError):
        return str(uuid.uuid4())

def registrar_rutas_en_supabase_db(app_instance):
    """Registra todas las rutas de la aplicación en Supabase"""
    from .utils.supabase_client import supabase
    import uuid
    
    rutas = []
    for rule in app_instance.url_map.iter_rules():
        blueprint_name = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'default_route'
        if blueprint_name == rule.endpoint and blueprint_name not in app_instance.blueprints:
            blueprint_name = 'app_level_route'

        rutas.append({
            "id": validar_o_generar_uuid(None),
            "ruta": rule.rule,
            "blueprint": blueprint_name,
            "metodo": ", ".join(sorted(list(rule.methods - {"HEAD", "OPTIONS"}))),
            "registrado_en": datetime.now().isoformat()
        })
    if rutas:
        try:
            response = supabase.table("rutas_registradas").upsert(rutas, on_conflict='ruta,metodo').execute()
            app_instance.logger.info(f"Rutas (re)insertadas/actualizadas en Supabase. Respuesta: {response}")
        except Exception as e:
            app_instance.logger.error(f"Error al (re)insertar/actualizar rutas en Supabase: {str(e)}", exc_info=True)

# Función para inicializar cron jobs con manejo de errores
def inicializar_cron_jobs_seguros(scheduler):
    """Wrapper seguro para inicializar trabajos cron"""
    try:
        from clientes.aura.scheduler_jobs import inicializar_cron_jobs
        inicializar_cron_jobs(scheduler)
        print("✅ Cron jobs inicializados correctamente")
    except Exception as e:
        print(f"⚠️ Error al inicializar cron jobs: {str(e)}")

def configure_logging():
    """Configura el sistema de logs con manejo seguro de archivos en Windows"""
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar handler con cierre adecuado para evitar bloqueos en Windows
    class SafeRotatingFileHandler(RotatingFileHandler):
        def doRollover(self):
            """Implementación segura para Windows que cierra el archivo antes de rotarlo"""
            if self.stream:
                self.stream.close()
                self.stream = None
            
            if os.path.exists(self.baseFilename + ".1"):
                try:
                    os.remove(self.baseFilename + ".1")
                except:
                    pass
                    
            if os.path.exists(self.baseFilename):
                try:
                    os.rename(self.baseFilename, self.baseFilename + ".1")
                except:
                    pass
                    
            self.mode = 'w'
            self.stream = self._open()
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Usar el handler seguro para Windows
    error_handler = SafeRotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(formatter)
    
    # Agregar handler al logger raíz
    logger.addHandler(error_handler)

def create_app(config_class=Config):
    """
    Función factory para crear y configurar la aplicación Flask
    """
    # Aplicar el parche para dump_cookie si no se ha hecho ya
    if not hasattr(werkzeug.http, '_patched_for_bytes'):
        werkzeug.http._patched_for_bytes = True
        werkzeug.http.dump_cookie = patched_dump_cookie
    
    # Crear la aplicación con la configuración básica
    import os
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'aura', 'templates')
    app = Flask(
        __name__,
        template_folder=template_path,  # OJO: esto es crítico
        static_folder='static'
    )
    
    # 🔧 APLICAR CONFIGURACIÓN - ¡ESTO ES LO QUE FALTABA!
    app.config.from_object(config_class)
    print(f"✅ Configuración aplicada: TEMPLATES_AUTO_RELOAD = {app.config.get('TEMPLATES_AUTO_RELOAD')}")
    
    # Configurar la clave secreta desde variable de entorno
    app.secret_key = os.environ.get("SECRET_KEY")

    try:
        initialize_app(app)
    except Exception as e:
        app.logger.exception(f"❌ Error crítico durante create_app: {str(e)}")
        if 'INITIALIZATION_ERRORS' in app.config:
            app.config['INITIALIZATION_ERRORS'].append(f"Error crítico en create_app: {str(e)}")
    # Ruta de inicialización para mostrar errores si existen
    @app.route('/initializing')
    def initializing():
        errors = app.config.get('INITIALIZATION_ERRORS', [])
        if errors:
            error_html = '<ul>' + ''.join(f'<li style="color:red">{e}</li>' for e in errors) + '</ul>'
        else:
            error_html = '<p class="text-green-600">Sin errores de inicialización.</p>'
        return f'''
        <html>
        <head><title>Inicializando AuraAI</title></head>
        <body style="font-family:sans-serif; background:#f9fafb;">
            <h2>Inicializando AuraAI...</h2>
            <div>{error_html}</div>
            <p>Esta página se actualizará automáticamente.</p>
            <script>setTimeout(()=>location.reload(), 5000);</script>
        </body>
        </html>
        '''
    print("✅ Aplicación Flask configurada correctamente")
    return app, socketio

# Reemplazar la función dump_cookie de Werkzeug con nuestra versión modificada
def patched_dump_cookie(key, value=None, *args, **kwargs):
    """
    Versión modificada de dump_cookie que maneja valores de tipo bytes.
    """
    if isinstance(value, bytes):
        try:
            value = value.decode('utf-8')
        except UnicodeDecodeError:
            value = value.hex()
    return original_dump_cookie(key, value, *args, **kwargs)

# Aplicar el parche a nivel global
werkzeug.http.dump_cookie = patched_dump_cookie

# Inicializar la aplicación
try:
    print("Inicializando aplicación AuraAi2...")
    app, socketio = create_app()
except Exception as e:
    print(f"❌ Error crítico en la inicialización: {str(e)}")
    # Crear una app mínima para evitar errores fatales
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_index():
        return f"Error crítico en la inicialización: {str(e)}"