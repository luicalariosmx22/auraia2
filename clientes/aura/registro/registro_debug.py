from clientes.aura.routes.debug_session import debug_session_bp

def registrar_blueprints_debug(app, safe_register_blueprint):
    safe_register_blueprint(app, debug_session_bp, url_prefix="/debug")
    # otros blueprints debug...
