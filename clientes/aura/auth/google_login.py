# clientes/aura/auth/google_login.py

from flask import Blueprint, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
import os

google_login_bp = Blueprint("google_login", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

@google_login_bp.route("/login")
def login():
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

    authorization_url, state = oauth.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="select_account"
    )

    session["oauth_state"] = state
    return redirect(authorization_url)

@google_login_bp.route("/login/google/callback")
def callback():
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        state=session.get("oauth_state")
    )

    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url,
    )

    resp = oauth.get(USER_INFO_URL)
    user_info = resp.json()

    session["email"] = user_info.get("email")
    session["name"] = user_info.get("name")
    session["user"] = {
        "picture": user_info.get("picture"),
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "id": user_info.get("id")  # ⚠️ Solo si viene de Google
    }

    from clientes.aura.utils.auth_utils import is_admin_user
    session["is_admin"] = is_admin_user(session["email"])

    return redirect(
        url_for("admin_dashboard.dashboard_admin")
        if session["is_admin"]
        else url_for("panel_cliente.panel_cliente")
    )
