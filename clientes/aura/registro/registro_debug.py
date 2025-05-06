from clientes.aura.routes.debug_verificar import debug_verificar_bp
from clientes.aura.routes.admin_debug_master import admin_debug_master_bp

def registrar_blueprints_debug(app, safe_register_blueprint):
    try:
        safe_register_blueprint(app, debug_verificar_bp)
        safe_register_blueprint(app, admin_debug_master_bp, url_prefix="/admin/debug")
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_debug: {e}")
