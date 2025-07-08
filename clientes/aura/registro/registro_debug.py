from clientes.aura.routes.debug_session import debug_session_bp
from clientes.aura.routes.debug_verificador import debug_verificador_bp

def registrar_blueprints_debug(app, safe_register_blueprint):
    safe_register_blueprint(app, debug_session_bp, url_prefix="/debug")
    safe_register_blueprint(app, debug_verificador_bp)
    # otros blueprints debug...
