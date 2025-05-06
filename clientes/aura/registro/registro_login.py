def registrar_blueprints_login(app):
    try:
        from clientes.aura.auth.login import login_bp
        if 'login' not in app.blueprints:
            app.register_blueprint(login_bp, name='login')
            print("✅ Login blueprint registrado")
        else:
            print("⚠️ Login blueprint ya estaba registrado.")
    except Exception as e:
        print("❌ Error en registrar_blueprints_login:", str(e))
