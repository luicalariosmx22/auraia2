def registrar_blueprints_admin(app):
    try:
        from clientes.aura.routes.admin_noras import admin_noras_bp
        from clientes.aura.routes.admin_nora import admin_nora_bp

        app.register_blueprint(admin_noras_bp)
        app.register_blueprint(admin_nora_bp)

        print("✅ Admin blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_admin:", str(e))
