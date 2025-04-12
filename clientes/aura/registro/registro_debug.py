def registrar_blueprints_debug(app):
    try:
        from clientes.aura.routes.debug_verificar import debug_verificar_bp
        from clientes.aura.routes.debug_env import debug_env_bp
        from clientes.aura.routes.debug_google import debug_google_bp
        from clientes.aura.routes.debug_routes import debug_routes_bp

        from clientes.aura.debug.debug_archivos import debug_archivos_bp
        from clientes.aura.debug.debug_mensaje_hola import debug_mensaje_hola_bp
        from clientes.aura.debug.debug_botdata_test import debug_test_bp  # opcional

        app.register_blueprint(debug_verificar_bp)
        app.register_blueprint(debug_env_bp)
        app.register_blueprint(debug_google_bp)
        app.register_blueprint(debug_routes_bp)

        app.register_blueprint(debug_archivos_bp)
        app.register_blueprint(debug_mensaje_hola_bp)
        app.register_blueprint(debug_test_bp)

        print("✅ Debug blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_debug:", str(e))
