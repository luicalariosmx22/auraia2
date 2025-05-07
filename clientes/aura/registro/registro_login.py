from clientes.aura.auth.login_google import login_bp  # 🛠 Importar blueprint de login desde el módulo correcto

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp)
