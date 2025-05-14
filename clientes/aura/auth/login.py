from flask import Blueprint, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
import os

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

# ========= Iniciar login =========
@login_bp.route("/login")
def login_google():
    if not GOOGLE_REDIRECT_URI:
        return "❌ ERROR: GOOGLE_REDIRECT_URI no está definido en variables de entorno."

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

    session["oauth_state"] = state
    return redirect(authorization_url)

# ========= Callback corregido =========
@login_bp.route("/login/google/callback")
def callback():
    print(f"DEBUG: Parámetros recibidos en el callback: {request.args}")

    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=GOOGLE_REDIRECT_URI,  # Usa la variable de entorno aquí
        state=session.get("oauth_state")
    )

    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url,
    )

    resp = oauth.get(USER_INFO_URL)
    user_info = resp.json()

    session["user"] = {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "picture": user_info.get("picture")
    }

    from clientes.aura.utils.auth_utils import is_admin_user
    session["is_admin"] = is_admin_user(session["user"]["email"])

    # Depuración: Verifica el contenido de la sesión
    print(f"✅ Sesión configurada: {session}")

    # ✅ Redirección segura usando ruta directa primero
    return redirect("/admin" if session["is_admin"] else "/panel_cliente")
