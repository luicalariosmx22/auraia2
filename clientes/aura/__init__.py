# clientes/aura/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session as flask_session, redirect, url_for, request, jsonify
from dotenv import load_dotenv
from .app_config import Config
from .extensions import socketio, session_ext, scheduler
from apscheduler.triggers.cron import CronTrigger

class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        if 'socket.io' in record.getMessage() and 'polling' in record.getMessage():
            return False
        return ' 200 -' not in record.getMessage()

def safe_register_blueprint(app, blueprint, **kwargs):
    """
    Registra un blueprint de forma segura, evitando duplicados.
    """
    unique_name = kwargs.pop("name", blueprint.name)
    if unique_name not in app.blueprints:
        app.register_blueprint(blueprint, name=unique_name, **kwargs)
        app.logger.info(f"✅ Blueprint '{unique_name}' registrado")
    else:
        app.logger.warning(f"⚠️ Blueprint ya estaba registrado: {unique_name}")

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    load_dotenv()
    app.config.from_object(config_class)

    app.session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")

    app.logger.info("🚀 APLICACIÓN FLASK CREADA Y CONFIGURACIÓN INICIAL CARGADA 🚀")

    session_ext.init_app(app)
    socketio.init_app(app)
    app.logger.info("Extensiones Flask-Session y Flask-SocketIO inicializadas.")

    if not app.debug:
        error_file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
        error_file_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        error_file_handler.setFormatter(error_formatter)
        app.logger.addHandler(error_file_handler)
        app.logger.info("Handler de logging para errores de app configurado (error.log).")

        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.addFilter(WerkzeugFilter())
        app.logger.info("Filtro de logging para Werkzeug añadido.")

        socketio_polling_log = logging.getLogger('socketio_polling_custom')
        socketio_polling_log.setLevel(logging.INFO)
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            socketio_polling_file_handler = RotatingFileHandler("logs/socketio_polling.log", maxBytes=100000, backupCount=3)
            socketio_polling_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            socketio_polling_log.addHandler(socketio_polling_file_handler)
            app.logger.info("Handler de logging para socketio_polling configurado (logs/socketio_polling.log).")
        except Exception as e:
            app.logger.error(f"No se pudo configurar el archivo de log para socketio_polling: {e}")

    logging.getLogger("twilio.http_client").setLevel(logging.WARNING)
    app.logger.info("Nivel de logging para twilio.http_client establecido a WARNING.")

    if not scheduler.running:
        from .tasks.meta_ads_reporter import enviar_reporte_semanal
        scheduler.add_job(
            func=enviar_reporte_semanal,
            trigger=CronTrigger(day_of_week='mon', hour=10, minute=0, timezone='America/Hermosillo'),
            id='job_enviar_reporte_semanal',
            name='Reporte Semanal Meta Ads Aura',
            replace_existing=True
        )
        try:
            scheduler.start()
            app.logger.info("APScheduler iniciado y trabajo 'enviar_reporte_semanal' añadido.")
        except Exception as e:
            app.logger.error(f"Error al iniciar APScheduler o añadir job: {e}", exc_info=True)
    else:
        app.logger.info("APScheduler ya estaba corriendo.")

    app.logger.info("Inicio de registro de Blueprints (aún por completar)...")

    from .utils.blueprint_utils_v2 import registrar_blueprints_login
    from .registro.registro_base import registrar_blueprints_base
    from .registro.registro_admin import registrar_blueprints_admin
    from .registro.registro_debug import registrar_blueprints_debug
    from .registro.registro_invitado import registrar_blueprints_invitado
    from .routes.panel_chat import panel_chat_bp
    from .routes.webhook import webhook_bp
    from .routes.admin_nora_dashboard import admin_nora_dashboard_bp
    from .routes.etiquetas import etiquetas_bp
    from .routes.panel_cliente import panel_cliente_bp
    from .routes.panel_cliente_contactos import panel_cliente_contactos_bp
    from .routes.admin_verificador_rutas import admin_verificador_bp
    from .routes.panel_cliente_envios import panel_cliente_envios_bp
    from .routes.admin_nora import admin_nora_bp
    from .routes.cliente_nora import cliente_nora_bp
    from .routes.cobranza import cobranza_bp
    from .routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
    from .routes.panel_cliente_ads import panel_cliente_ads_bp

    registrar_blueprints_login(app, safe_register_blueprint)
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
        (panel_cliente_ads_bp, f"/panel_cliente/{{nombre_nora}}/ads"),
    ]

    for blueprint, prefix in blueprints_estaticos:
        safe_register_blueprint(app, blueprint, url_prefix=prefix)

    app.register_blueprint(cobranza_bp, url_prefix="/api")

    app.logger.info("Inicio de definición de rutas de app (aún por completar)...")
    @app.route("/")
    def home():
        if "user" not in flask_session:
            return redirect(url_for("login_bp.login_google"))
        if flask_session.get("is_admin"):
            return redirect(url_for("admin_nora_dashboard_bp.dashboard_admin"))
        else:
            return redirect(url_for("panel_cliente_bp.configuracion_cliente", nombre_nora=flask_session.get("nombre_nora", "aura")))

    @app.route("/logout")
    def logout():
        flask_session.clear()
        return redirect(url_for("login_bp.login_google"))

    @app.route('/debug_info', methods=['GET'])
    def debug_info():
        return jsonify({
            "rutas_registradas": [rule.rule for rule in app.url_map.iter_rules()],
            "estado": "OK",
        })

    @app.route('/healthz')  # Ruta de health check
    def health_check():
        return "OK", 200

    @app.route('/healthz_factory')
    def health_check_factory():
        return "OK from factory", 200

    app.logger.info("Inicio de handlers before_request (aún por completar)...")
    @app.before_request
    def log_polling_requests():
        if request.path.startswith('/socket.io') and request.args.get('transport') == 'polling':
            app.logger.info(f"{request.remote_addr} - {request.method} {request.full_path}")

    app.logger.info(f"📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")
    app.logger.info("Función create_app completada (parcialmente).")
    return app