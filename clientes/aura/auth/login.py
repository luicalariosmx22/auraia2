# clientes/aura/auth/login.py

from flask import Blueprint, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
import os

login_bp = Blueprint("login", __name__)

# Cargar variables de entorno necesarias
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # Ej: https://app.soynoraai.com/callback

# Scopes solicitados para acceder al perfil del usuario
SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

# URLs de endpoints de Google OAuth
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

# ========= Ruta para iniciar sesión =========
@login_bp.route("/login")
def login_google():
    oauth = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL, access_type="offline", prompt="select_account")

    session["oauth_state"] = state
    return redirect(authorization_url)

# ========= Callback después del login =========
@login_bp.route("/callback")
def callback():
    oauth = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=REDIRECT_URI, state=session.get("oauth_state"))
    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url,
    )

    # Obtener información del usuario
    resp = oauth.get(USER_INFO_URL)
    user_info = resp.json()

    session["user"] = {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "picture": user_info.get("picture")
    }

    # Dar acceso de admin si el correo está en la lista
    from clientes.aura.utils.auth_utils import is_admin_user
    session["is_admin"] = is_admin_user(session["user"]["email"])

    return redirect(url_for("panel_chat.panel_chat") if session["is_admin"] else url_for("panel_cliente.panel_cliente"))
