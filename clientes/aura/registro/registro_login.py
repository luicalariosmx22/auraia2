from flask import Blueprint

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/google", methods=["GET", "POST"])
def login_google():
    # Lógica para el login con Google
    pass

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp, url_prefix="/login")
