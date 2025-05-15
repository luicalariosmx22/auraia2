from flask import Blueprint, redirect, request, session, url_for, render_template
from requests_oauthlib import OAuth2Session
import os
from clientes.aura.utils.supabase_client import supabase

print("DEBUG: Este es el archivo login.py que se está ejecutando")

# Blueprint sin prefijo para que funcione /login y /login/google/callback
login_bp = Blueprint("login", __name__)

# Cargar variables de entorno
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # Usa la variable de entorno aquí

SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

# ========= Mostrar pantalla login =========
@login_bp.route("/login")
def login_screen():
    return render_template("login_google.html")

# ========= Iniciar login =========
@login_bp.route("/login/start")
def login_google():
    print("DEBUG: Entrando a login_google")
    
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=GOOGLE_REDIRECT_URI,  # Usa la variable de entorno aquí
        scope=SCOPE
    )

    authorization_url, state = oauth.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="select_account"
    )

    print(f"DEBUG: URL de autenticación generada: {authorization_url}")
    session["oauth_state"] = state
    return redirect(authorization_url)

# ========= Callback corregido =========
@login_bp.route("/login/google/callback")
def login_callback():
    try:
        from clientes.aura.utils.google_auth import get_google_auth
        google = get_google_auth(state=session.get("state"))
        token = google.fetch_token(
            "https://accounts.google.com/o/oauth2/token",
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            authorization_response=request.url,
        )
        session["token"] = token
        google = get_google_auth(token=token)
        resp = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
        user_info = resp.json()

        correo = user_info.get("email")
        result = supabase.table("configuracion_bot").select("*").eq("correo_cliente", correo).execute()

        if not result.data:
            return "❌ Este correo no tiene acceso autorizado.", 403

        datos = result.data[0]

        session.permanent = True  # ✅ ACTIVA SESIÓN PERMANENTE

        session["user"] = {
            "name": user_info.get("name"),
            "email": correo,
            "picture": user_info.get("picture")
        }
        session["is_admin"] = datos.get("tipo_usuario") == "admin"
        session["nombre_nora"] = datos["nombre_nora"]

        return redirect(
            url_for("admin_dashboard.dashboard_admin")
            if session.get("is_admin")
            else url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=session.get("nombre_nora"))
        )

    except Exception as e:
        return f"Error en login: {str(e)}"
