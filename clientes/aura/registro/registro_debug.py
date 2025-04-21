def registrar_blueprints_debug(app):
    try:
        from clientes.aura.routes.debug_verificar import debug_verificar_bp
        app.register_blueprint(debug_verificar_bp)
        print("✅ Debug blueprint 'debug_verificar_bp' registrado")

        from clientes.aura.routes.admin_debug_master import admin_debug_master_bp
        app.register_blueprint(admin_debug_master_bp, url_prefix="/admin/debug")
        print("✅ Debug blueprint 'admin_debug_master_bp' registrado")
    except Exception as e:
        print("❌ Error en registrar_blueprints_debug:", str(e))
