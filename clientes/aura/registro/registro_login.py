import os
from flask import Blueprint, request, redirect, url_for, render_template

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/google", methods=["GET", "POST"])
def login_google():
    try:
        print("DEBUG: Entrando a login_google")
        if request.method == "GET":
            # Renderiza el HTML con el botón para iniciar sesión con Google
            return render_template("login_google.html")
        elif request.method == "POST":
            # Obtén las variables de entorno
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
            if not client_id or not redirect_uri:
                raise ValueError("GOOGLE_CLIENT_ID o GOOGLE_REDIRECT_URI no están configurados")

            # Genera la URL de autenticación de Google
            google_auth_url = (
                f"https://accounts.google.com/o/oauth2/auth"
                f"?client_id={client_id}"
                f"&redirect_uri={redirect_uri}"
                f"&response_type=code"
                f"&scope=email profile"
            )
            print(f"DEBUG: URL de autenticación generada: {google_auth_url}")
            return redirect(google_auth_url)
    except Exception as e:
        print(f"ERROR: Fallo en login_google: {e}")
        return f"❌ Error en login_google: {e}", 500

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp, url_prefix="/login")
