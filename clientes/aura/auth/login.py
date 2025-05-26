from flask import Blueprint, redirect, request, session, url_for, render_template
from supabase import create_client
from requests_oauthlib import OAuth2Session
import os

login_bp = Blueprint("login", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

def get_google_auth(token=None, state=None):
    if token:
        return OAuth2Session(GOOGLE_CLIENT_ID, token=token)
    if state:
        return OAuth2Session(GOOGLE_CLIENT_ID, state=state, redirect_uri=REDIRECT_URI)

    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]
    return OAuth2Session(GOOGLE_CLIENT_ID, scope=scope, redirect_uri=REDIRECT_URI)

@login_bp.route("/")
def login():
    return render_template("login.html")

@login_bp.route("/start")
def login_start():
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        access_type="offline", prompt="select_account")
    session["state"] = state
    return redirect(auth_url)

@login_bp.route("/google/callback")
def login_callback():
    try:
        google = get_google_auth(state=session.get("state"))
        token = google.fetch_token(
            "https://accounts.google.com/o/oauth2/token",
            client_secret=GOOGLE_CLIENT_SECRET,
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

        session.permanent = True  # 🔐 mantiene la sesión entre vistas

        session["email"] = user_info.get("email")
        session["name"] = user_info.get("name")
        session["is_admin"] = str(datos.get("tipo_usuario", "")).lower() == "admin"
        session["nombre_nora"] = datos["nombre_nora"]

        session["user"] = {
            "id": datos.get("id", ""),
            "nombre": datos.get("nombre", "Desconocido"),
            "nombre_nora": datos.get("nombre_nora", ""),
            "empresa_id": datos.get("empresa_id", ""),
            "cliente_id": datos.get("cliente_id", "")
        }

        print("🎯 Sesión establecida:")
        print("email:", session.get("email"))
        print("nombre_nora:", session.get("nombre_nora"))
        print("is_admin:", session.get("is_admin"))

        # ✅ Evalúa is_admin como string por seguridad
        valor_admin = session.get("is_admin")
        print("🧪 Valor crudo de is_admin:", valor_admin)

        if str(valor_admin).lower() == "true":
            return redirect(url_for("admin_dashboard.dashboard_admin"))
        elif session.get("nombre_nora"):
            return redirect(url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=session.get("nombre_nora")))
        else:
            return redirect("/login")  # fallback en caso de error

    except Exception as e:
        return f"Error en login: {str(e)}"
