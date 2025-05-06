def registrar_blueprints_debug(app):
    try:
        from clientes.aura.routes.debug_verificar import debug_verificar_bp
        app.register_blueprint(debug_verificar_bp, name="debug_verificar_bp_unique")
        print("✅ Debug blueprint 'debug_verificar_bp' registrado con name='debug_verificar_bp_unique'")

        from clientes.aura.routes.admin_debug_master import admin_debug_master_bp
        app.register_blueprint(admin_debug_master_bp, url_prefix="/admin/debug", name="admin_debug_master_bp_unique")
        print("✅ Debug blueprint 'admin_debug_master_bp' registrado con name='admin_debug_master_bp_unique'")
    except Exception as e:
        print("❌ Error en registrar_blueprints_debug:", str(e))
