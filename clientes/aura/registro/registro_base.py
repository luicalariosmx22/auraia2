def registrar_blueprints_base(app):
    try:
        from clientes.aura.auth.login import login_bp
        from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
        from clientes.aura.routes.webhook import webhook_bp

        app.register_blueprint(login_bp)
        app.register_blueprint(admin_dashboard_bp)
        app.register_blueprint(webhook_bp)

        print("✅ Base blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_base:", str(e))
