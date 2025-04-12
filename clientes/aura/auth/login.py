# clientes/aura/auth/login.py

from flask import Blueprint, redirect, request, session, url_for
import os
import requests
from requests_oauthlib import OAuth2Session
from clientes.aura.utils.auth_utils import is_admin_user

login_bp = Blueprint("login", __name__)

# Configuración de Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

SCOPE = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

# Ruta para iniciar login
@login_bp.route("/login")
def login_google():
    google = OAuth2Session(GOOGLE_CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL, access_type="offline", prompt="select_account")
    session["oauth_state"] = state
    return redirect(authorization_url)

# Callback
@login_bp.route("/login/callback")
def callback():
    google = OAuth2Session(GOOGLE_CLIENT_ID, state=session["oauth_state"], redirect_uri=REDIRECT_URI)
    token = google.fetch_token(TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url)
    session["oauth_token"] = token

    # Obtener información del usuario
    resp = google.get(USER_INFO_URL)
    user_info = resp.json()

    session["user"] = {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "picture": user_info.get("picture")
    }

    # Aquí usamos la función modular
    session["is_admin"] = is_admin_user(user_info.get("email"))

    return redirect(url_for("home"))
