# clientes/aura/routes/debug_google.py
import os
from flask import Blueprint, jsonify, request
from oauthlib.oauth2 import WebApplicationClient
import requests

debug_google_bp = Blueprint("debug_google", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@debug_google_bp.route("/debug/google_status")
def google_status():
    try:
        if not GOOGLE_CLIENT_ID:
            return jsonify({"error": "GOOGLE_CLIENT_ID no está definido en el entorno"}), 500

        provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        auth_url = client.prepare_request_uri(
            provider_cfg["authorization_endpoint"],
            redirect_uri=request.url_root + "login/google/callback",
            scope=["openid", "email", "profile"]
        )

        return jsonify({
            "google_discovery_url_status": "ok",
            "authorization_endpoint": provider_cfg["authorization_endpoint"],
            "generated_login_url": auth_url,
            "redirect_uri": request.url_root + "login/google/callback"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
