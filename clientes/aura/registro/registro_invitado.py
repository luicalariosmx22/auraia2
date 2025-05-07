def registrar_blueprints_invitado(app, safe_register_blueprint):  # 🛠 Added safe_register_blueprint as an argument
    try:
        from clientes.aura.routes.landing import landing_bp
        safe_register_blueprint(app, landing_bp)  # 🛠 Use safe_register_blueprint instead of app.register_blueprint

        print("✅ Invitado blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_invitado:", str(e))
