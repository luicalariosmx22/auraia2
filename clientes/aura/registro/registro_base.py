from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
from clientes.aura.routes.webhook import webhook_bp

def registrar_blueprints_base(app, safe_register_blueprint):
    try:
        safe_register_blueprint(app, admin_dashboard_bp)
        safe_register_blueprint(app, webhook_bp)
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_base: {e}")
