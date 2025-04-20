def registrar_blueprints_debug(app):
    try:
        from clientes.aura.routes.debug_verificar import debug_verificar_bp
        app.register_blueprint(debug_verificar_bp)
        print("✅ Debug blueprint registrado")
    except Exception as e:
        print("❌ Error en registrar_blueprints_debug:", str(e))
