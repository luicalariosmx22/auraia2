from clientes.aura.utils.blueprint_utils import safe_register_blueprint

def registrar_blueprints_base(app):
    try:
        from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
        from clientes.aura.routes.webhook import webhook_bp

        if 'admin_dashboard' not in app.blueprints:
            safe_register_blueprint(app, admin_dashboard_bp)
            print("✅ Blueprint 'admin_dashboard' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'admin_dashboard' ya estaba registrado.")

        if 'webhook' not in app.blueprints:
            safe_register_blueprint(app, webhook_bp)
            print("✅ Blueprint 'webhook' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'webhook' ya estaba registrado.")

    except Exception as e:
        print("❌ Error en registrar_blueprints_base:", str(e))
