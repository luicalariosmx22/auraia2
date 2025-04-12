# clientes/aura/routes/debug_google.py

from flask import Blueprint, render_template, session
from requests_oauthlib import OAuth2Session
import os

debug_google_bp = Blueprint("debug_google", __name__)

@debug_google_bp.route("/debug/google", methods=["GET"])
def verificar_login_google():
    errores = []
    detalles = {}

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

    if not GOOGLE_CLIENT_ID:
        errores.append("❌ Falta GOOGLE_CLIENT_ID")
    if not GOOGLE_CLIENT_SECRET:
        errores.append("❌ Falta GOOGLE_CLIENT_SECRET")
    if not GOOGLE_REDIRECT_URI:
        errores.append("❌ Falta GOOGLE_REDIRECT_URI")

    detalles["GOOGLE_CLIENT_ID"] = GOOGLE_CLIENT_ID or "❌ No definido"
    detalles["GOOGLE_REDIRECT_URI"] = GOOGLE_REDIRECT_URI or "❌ No definido"

    url_generada = None
    estado = "⚠️ No generada"

    if not errores:
        try:
            oauth = OAuth2Session(
                GOOGLE_CLIENT_ID,
                redirect_uri=GOOGLE_REDIRECT_URI,
                scope=[
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "openid"
                ]
            )

            auth_url, state = oauth.authorization_url(
                "https://accounts.google.com/o/oauth2/auth",
                access_type="offline",
                prompt="select_account"
            )

            session["oauth_state"] = state
            url_generada = auth_url
            estado = "✅ Generada correctamente"

        except Exception as e:
            errores.append(f"❌ Error generando URL de login: {str(e)}")

    return render_template(
        "debug_google.html",
        detalles=detalles,
        errores=errores,
        auth_url=url_generada,
        estado=estado
    )
