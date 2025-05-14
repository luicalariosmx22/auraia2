from flask import Blueprint, request, redirect, url_for

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/google", methods=["GET", "POST"])
def login_google():
    print("DEBUG: Entrando a login_google")
    if request.method == "GET":
        # Redirige al flujo de autenticación de Google
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            "?client_id=TU_CLIENT_ID"
            "&redirect_uri=TU_REDIRECT_URI"
            "&response_type=code"
            "&scope=email profile"
        )
        return redirect(google_auth_url)
    elif request.method == "POST":
        # Maneja la respuesta de Google después de la autenticación
        return redirect(url_for("home"))

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp, url_prefix="/login")
