from clientes.aura.routes.login import login_bp  # 🛠 Importar blueprint de login

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp)
