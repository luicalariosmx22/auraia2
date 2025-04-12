def registrar_blueprints_login(app):
    try:
        from clientes.aura.auth.login import login_bp
        app.register_blueprint(login_bp)
        print("✅ Login blueprint registrado")
    except Exception as e:
        print("❌ Error en registrar_blueprints_login:", str(e))
