import os
import json
import requests
from flask import Blueprint, redirect, url_for, session, request
from oauthlib.oauth2 import WebApplicationClient
from dotenv import load_dotenv

load_dotenv()

google_login_bp = Blueprint("google_login", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@google_login_bp.route("/login/google")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # 🔒 Forzar HTTPS en producción
    redirect_uri = "https://app.soynoraai.com/login/google/callback"

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@google_login_bp.route("/login/google/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    redirect_uri = "https://app.soynoraai.com/login/google/callback"

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=redirect_uri,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        user_email = userinfo_response.json()["email"]

        session["user"] = {
            "email": user_email,
            "name": userinfo_response.json()["name"],
            "picture": userinfo_response.json()["picture"],
        }

        admin_emails = ["bluetiemx@gmail.com", "soynoraai@gmail.com"]
        session["is_admin"] = user_email in admin_emails

        return redirect(url_for("panel_chat.panel_chat"))
    else:
        return "Usuario no verificado", 400

@google_login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))
