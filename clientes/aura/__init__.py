# clientes/aura/__init__.py
from flask import Flask, redirect, url_for, session, request, jsonify
from .app_config import Config
from .extensions import socketio, session_ext, scheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from logging.handlers import RotatingFileHandler

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
    app.config.from_object(config_class)

    # Inicializar extensiones
    socketio.init_app(app)
    session_ext.init_app(app)

    # Configurar Logging
    if not app.debug:
        file_handler = RotatingFileHandler("error.log", maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.info("Logging configurado para errores de la aplicación.")

    logging.getLogger("twilio.http_client").setLevel(logging.WARNING)

    # Registrar Tareas APScheduler
    if not scheduler.running:
        from .tasks.meta_ads_reporter import enviar_reporte_semanal
        scheduler.add_job(
            func=enviar_reporte_semanal,
            trigger=CronTrigger(day_of_week='mon', hour=10, minute=0, timezone='America/Hermosillo'),
            id='job_enviar_reporte_semanal',
            name='Reporte Semanal Meta Ads Aura',
            replace_existing=True
        )
        scheduler.start()
        app.logger.info("APScheduler iniciado y trabajo 'enviar_reporte_semanal' añadido.")

    # Registrar Blueprints
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

    # Rutas de Nivel de Aplicación
    @app.route("/")
    def home():
        if "user" not in session:
            return redirect(url_for("login_bp.login_google"))
        if session.get("is_admin"):
            return redirect(url_for("admin_nora_dashboard_bp.dashboard_admin"))
        else:
            return redirect(url_for("panel_cliente_bp.configuracion_cliente", nombre_nora=session.get("nombre_nora", "aura")))

    @app.route("/logout")
    def logout():
        session.clear()
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

    # before_request handler
    @app.before_request
    def log_polling_requests():
        if request.path.startswith('/socket.io') and request.args.get('transport') == 'polling':
            app.logger.info(f"{request.remote_addr} - {request.method} {request.full_path}")

    app.logger.info(f"📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")
    return app