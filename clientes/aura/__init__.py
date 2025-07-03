# clientes/aura/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session, redirect, url_for, request, jsonify  # ← CAMBIO AQUÍ
from flask_session import Session
from dotenv import load_dotenv

# Tus módulos modulares
from .app_config import Config
from .extensiones import socketio, session_ext, scheduler # ¡Corregido a 'extensiones.py'!

# Para APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

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
from .routes.panel_cliente_contactos import panel_cliente_contactos_bp
from .routes.panel_cliente_envios import panel_cliente_envios_bp
from .routes.admin_nora import admin_nora_bp
from .routes.admin_noras import admin_noras_bp # Lo tenías en app.py original
from .routes.cliente_nora import cliente_nora_bp
print("✅ cliente_nora_bp importado correctamente")
# ✅ panel_cliente_conocimiento removido - ahora está integrado en admin_nora
from .routes.panel_cliente_ads import panel_cliente_ads_bp
print("✅ panel_cliente_ads_bp importado correctamente")
from .routes.cobranza import cobranza_bp
print("✅ cobranza_bp importado correctamente")
# ✅ panel_cliente_etiquetas_conocimiento removido - ahora está integrado en admin_nora
from clientes.aura.routes.panel_team.vista_panel_team import panel_team_bp # Nueva importación
print("✅ panel_team_bp importado correctamente")
from clientes.aura.routes.panel_cliente_pagos.vista_presupuestos import panel_cliente_pagos_presupuestos_bp # Nueva importación
print("✅ panel_cliente_pagos_presupuestos_bp importado correctamente")
from clientes.aura.routes.panel_cliente_pagos.vista_presupuesto_nuevo import panel_cliente_pagos_presupuesto_nuevo_bp # Nueva importación
print("✅ panel_cliente_pagos_presupuesto_nuevo_bp importado correctamente")
from clientes.aura.routes.panel_cliente_tareas.tareas_completadas import panel_tareas_completadas_bp # Nueva importación
print("✅ panel_tareas_completadas_bp importado correctamente")
from clientes.aura.routes.reportes_meta_ads import reportes_meta_ads_bp # Nueva importación (con lazy loading)
print("✅ reportes_meta_ads_bp importado correctamente (optimizado)")
from clientes.aura.routes.campanas_meta_ads import campanas_meta_ads_bp # Nueva importación
print("✅ campanas_meta_ads_bp importado correctamente")

# Para la lógica de blueprints dinámicos
from .utils.supabase_client import supabase
import uuid # Para validar_o_generar_uuid
from datetime import datetime # Para registrar_rutas_en_supabase

from clientes.aura.scheduler_jobs import inicializar_cron_jobs

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
    import logging
    app.logger.setLevel(logging.DEBUG)  # Fuerza nivel de log global
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

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
    
    # 🍪 CONFIGURACIÓN ESPECÍFICA PARA COOKIES DE NAVEGADOR
    app.config['SESSION_COOKIE_HTTPONLY'] = False  # Permitir acceso desde JavaScript para debug
    app.config['SESSION_COOKIE_SECURE'] = False    # No requerir HTTPS para desarrollo local
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Permitir cookies en requests de navegador
    app.config['SESSION_PERMANENT'] = True         # Hacer sesiones permanentes
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
    print("🍪 Configuración de cookies optimizada para navegador")
    
    # --- FIN DE CAMBIOS PARA DEPURACIÓN ---

    print("🚀 Aplicación Flask creada y configuración inicial cargada por la factory.")

    # --- Agrega esto en tu create_app o donde creas la app Flask principal ---
    # Esto fuerza a Flask a respetar el protocolo https cuando está detrás de un proxy (como Railway)
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        print("ProxyFix y PREFERRED_URL_SCHEME configurados para https.")
    except Exception as e:
        print(f"[WARN] No se pudo aplicar ProxyFix: {e}")

    # Inicializar extensiones
    Session(app)  # Activa correctamente Flask-Session with SESSION_TYPE = filesystem
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

    logging.getLogger("httpx").setLevel(logging.WARNING)  # Oculta los logs debug de Supabase

    # Registrar Tareas APScheduler
    if not scheduler.running:
        try:
            inicializar_cron_jobs(scheduler)
            scheduler.start()
            print("APScheduler iniciado y cron jobs registrados correctamente.")
        except Exception as e:
            print(f"Error al iniciar APScheduler: {e}")
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

    # Registrar blueprints de tareas (panel_cliente_tareas)
    from clientes.aura.routes.panel_cliente_tareas import register_tareas_blueprints
    register_tareas_blueprints(app)

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

    # Nueva línea para registrar el blueprint del panel de team
    safe_register_blueprint(app, panel_team_bp, url_prefix="/panel_team")
    # Registrar blueprint de presupuestos con url_prefix correcto (sin <nombre_nora> en el prefix)
    safe_register_blueprint(app, panel_cliente_pagos_presupuestos_bp, url_prefix="/panel_cliente")
    # Registrar blueprint para crear nuevo presupuesto
    safe_register_blueprint(app, panel_cliente_pagos_presupuesto_nuevo_bp, url_prefix="/panel_cliente")
    # Registrar blueprint para tareas completadas
    safe_register_blueprint(app, panel_tareas_completadas_bp, url_prefix="/panel_cliente")
    # --- Registrar Blueprints de reportes y campañas Meta Ads ---
    safe_register_blueprint(app, reportes_meta_ads_bp, url_prefix="/panel_cliente/<nombre_nora>/meta_ads")
    print("✅ reportes_meta_ads_bp registrado correctamente (optimizado)")
    safe_register_blueprint(app, campanas_meta_ads_bp, url_prefix="/panel_cliente/<nombre_nora>/meta_ads/campanas")
    
    # Google Ads se registra dinámicamente en registro_dinamico.py por módulo
    # # Registrar blueprint de Google Ads panel cliente (nuevo panel similar a Meta Ads)
    # from clientes.aura.routes.panel_cliente_google_ads import panel_cliente_google_ads_bp
    # safe_register_blueprint(app, panel_cliente_google_ads_bp, url_prefix="/panel_cliente/<nombre_nora>/google_ads")
    
    # Registrar blueprint para la API de Google Ads (temporalmente deshabilitado para diagnóstico)
    print("⚠️  Saltando carga de blueprint de Google Ads para diagnóstico...")
    # try:
    #     from routes.google_ads import google_ads_bp
    #     print("✅ Blueprint de Google Ads importado correctamente")
    #     safe_register_blueprint(app, google_ads_bp)
    #     print("✅ Blueprint de Google Ads API (google_ads_bp) registrado correctamente")
    # except ImportError as e:
    #     print(f"❌ Error al importar el blueprint de Google Ads API: {e}")
    # except Exception as e:
    #     print(f"❌ Error al registrar el blueprint de Google Ads API: {e}")

    # --- Registrar Blueprint Cliente Nora (Panel de Entrenamiento) ---
    print("Registrando blueprint cliente_nora_bp...")
    safe_register_blueprint(app, cliente_nora_bp, url_prefix="")
    print("✅ Blueprint cliente_nora_bp registrado correctamente")

    # --- Rutas de Nivel de Aplicación ---
    print("Definiendo rutas de nivel de aplicación...")
    
    print("Definiendo ruta raíz (/)")
    @app.route("/")
    def index():
        from flask import redirect, url_for, session
        print(f"🏠 ACCESO A RAÍZ - Host: {request.host}")
        print(f"🍪 Sesión actual: {dict(session)}")
        session.clear()  # Limpia cualquier sesión previa
        print(f"🧹 Sesión limpiada, redirigiendo a login")
        return redirect("/login/simple")

    print("Definiendo ruta logout (/logout)")
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login/simple")
    
    print("Definiendo ruta pública para reportes compartidos...")
    @app.route("/reporte_publico/<reporte_id>")
    def vista_reporte_publico(reporte_id):
        """
        Vista pública para reportes compartidos de Meta Ads.
        No requiere autenticación.
        """
        from flask import request as flask_request, render_template_string
        
        token = flask_request.args.get('token')
        if not token:
            return "Token requerido", 403
        
        try:
            # Verificar que el reporte existe
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
            if not reporte:
                return "Reporte no encontrado", 404
            
            # Opcional: Verificar token en tabla de reportes compartidos
            # Por simplicidad, mostramos el reporte si existe
            
            # Obtener anuncios detallados
            anuncios = supabase.table('meta_ads_anuncios_detalle') \
                .select('*') \
                .eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']) \
                .eq('fecha_inicio', reporte['fecha_inicio']) \
                .eq('fecha_fin', reporte['fecha_fin']) \
                .execute().data or []
            
            # Template simple para vista pública
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Reporte Meta Ads - {{ empresa_nombre }}</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <script src="https://cdn.tailwindcss.com"></script>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            </head>
            <body class="bg-gray-50">
                <div class="max-w-6xl mx-auto py-10 px-4">
                    <div class="text-center mb-8">
                        <h1 class="text-3xl font-bold text-gray-800">📊 Reporte Meta Ads</h1>
                        <p class="text-gray-600 mt-2">{{ empresa_nombre }}</p>
                        <p class="text-sm text-gray-500">Período: {{ fecha_inicio }} a {{ fecha_fin }}</p>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h2 class="text-xl font-semibold mb-4">📈 Resumen Ejecutivo</h2>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div class="text-center p-4 bg-blue-50 rounded">
                                <div class="text-2xl font-bold text-blue-600">${{ "%.2f"|format(importe_gastado_anuncios or 0) }}</div>
                                <div class="text-sm text-gray-600">Gasto Total</div>
                            </div>
                            <div class="text-center p-4 bg-green-50 rounded">
                                <div class="text-2xl font-bold text-green-600">{{ "{:,}"|format(impresiones or 0) }}</div>
                                <div class="text-sm text-gray-600">Impresiones</div>
                            </div>
                            <div class="text-center p-4 bg-purple-50 rounded">
                                <div class="text-2xl font-bold text-purple-600">{{ "{:,}"|format(alcance or 0) }}</div>
                                <div class="text-sm text-gray-600">Alcance</div>
                            </div>
                            <div class="text-center p-4 bg-orange-50 rounded">
                                <div class="text-2xl font-bold text-orange-600">{{ "{:,}"|format(clicks or 0) }}</div>
                                <div class="text-sm text-gray-600">Clicks</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">📱 Por Plataforma</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="p-4 border-l-4 border-blue-500">
                                <h3 class="font-semibold text-blue-700">📘 Facebook</h3>
                                <p class="text-lg font-bold">${{ "%.2f"|format(facebook_importe_gastado or 0) }}</p>
                                <p class="text-sm text-gray-600">{{ "{:,}"|format(facebook_impresiones or 0) }} impresiones</p>
                            </div>
                            <div class="p-4 border-l-4 border-pink-500">
                                <h3 class="font-semibold text-pink-700">📷 Instagram</h3>
                                <p class="text-lg font-bold">${{ "%.2f"|format(instagram_importe_gastado or 0) }}</p>
                                <p class="text-sm text-gray-600">{{ "{:,}"|format(instagram_impresiones or 0) }} impresiones</p>
                            </div>
                        </div>
                    </div>
                    
                    {% if anuncios %}
                    <div class="bg-white rounded-lg shadow-lg p-6 mt-8">
                        <h2 class="text-xl font-semibold mb-4">🎯 Top Anuncios</h2>
                        <div class="overflow-x-auto">
                            <table class="min-w-full text-sm">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-2 text-left">Anuncio</th>
                                        <th class="px-4 py-2 text-left">Plataforma</th>
                                        <th class="px-4 py-2 text-left">Gasto</th>
                                        <th class="px-4 py-2 text-left">Impresiones</th>
                                        <th class="px-4 py-2 text-left">Clicks</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for anuncio in anuncios[:10] %}
                                    <tr class="border-b">
                                        <td class="px-4 py-2">{{ anuncio.ad_name or anuncio.ad_id }}</td>
                                        <td class="px-4 py-2">
                                            {% if anuncio.publisher_platform == 'facebook' %}
                                                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">📘 FB</span>
                                            {% elif anuncio.publisher_platform == 'instagram' %}
                                                <span class="px-2 py-1 bg-pink-100 text-pink-800 rounded text-xs">📷 IG</span>
                                            {% else %}
                                                <span class="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">{{ anuncio.publisher_platform }}</span>
                                            {% endif %}
                                        </td>
                                        <td class="px-4 py-2 font-mono">${{ "%.2f"|format(anuncio.importe_gastado or 0) }}</td>
                                        <td class="px-4 py-2">{{ "{:,}"|format(anuncio.impresiones or 0) }}</td>
                                        <td class="px-4 py-2">{{ anuncio.clicks or 0 }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    <div class="text-center text-gray-500 text-sm mt-8">
                        <p>🔗 Reporte generado por AuraAI</p>
                        <p>{{ reporte_id }}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return render_template_string(
                template,
                empresa_nombre=reporte.get('empresa_nombre', 'Cliente'),
                fecha_inicio=reporte.get('fecha_inicio'),
                fecha_fin=reporte.get('fecha_fin'),
                importe_gastado_anuncios=reporte.get('importe_gastado_anuncios', 0),
                impresiones=reporte.get('impresiones', 0),
                alcance=reporte.get('alcance', 0),
                clicks=reporte.get('clicks', 0),
                facebook_importe_gastado=reporte.get('facebook_importe_gastado', 0),
                facebook_impresiones=reporte.get('facebook_impresiones', 0),
                instagram_importe_gastado=reporte.get('instagram_importe_gastado', 0),
                instagram_impresiones=reporte.get('instagram_impresiones', 0),
                anuncios=anuncios,
                reporte_id=reporte_id
            )
            
        except Exception as e:
            print(f"[ERROR] Error en vista pública: {e}")
            return f"Error al cargar reporte: {e}", 500
    
    print("Definiendo before_request handler...")
    # --- before_request handler ---
    @app.before_request
    def proteger_rutas_admin():
        ruta = request.path
        if ruta.startswith("/admin") and not session.get("is_admin", False):
            return redirect("/login/simple")
        if request.path.startswith('/socket.io') and request.args.get('transport') == 'polling':
            socketio_polling_logger = logging.getLogger('socketio_polling_custom')
            socketio_polling_logger.info(f"{request.remote_addr} - {request.method} {request.full_path}")

    print("✅ Rutas de nivel de aplicación definidas")

    # Iniciar cron de tareas recurrentes de forma asíncrona
    print("Iniciando cron de tareas recurrentes...")
    try:
        import threading
        def iniciar_cron_async():
            try:
                from clientes.aura.cron.tareas_recurrentes import iniciar_cron_recurrentes
                iniciar_cron_recurrentes()
                print("✅ Cron de tareas recurrentes iniciado correctamente")
            except Exception as e:
                print(f"❌ Error al iniciar el cron de tareas recurrentes: {e}")
        
        # Ejecutar en un hilo separado para no bloquear la aplicación
        cron_thread = threading.Thread(target=iniciar_cron_async, daemon=True)
        cron_thread.start()
        print("🔄 Cron iniciado en hilo separado")
    except Exception as e:
        print(f"❌ Error al configurar el cron de tareas recurrentes: {e}")

    print("✅ Aplicación Flask configurada completamente")
    return app