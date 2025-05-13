from clientes.aura.auth.google_login import google_login_bp  # ✅ Corregido: nombre de archivo y nombre de blueprint

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, google_login_bp)
