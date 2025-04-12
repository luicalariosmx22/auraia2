# clientes/aura/routes/debug_google.py

from flask import Blueprint, render_template, session
from requests_oauthlib import OAuth2Session
import os
import requests

debug_google_bp = Blueprint("debug_google", __name__)

@debug_google_bp.route("/debug/google", methods=["GET"])
def verificar_login_google():
    errores = []
    detalles = {}

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    URI_ESPERADO = "https://app.soynoraai.com/login/google/callback"

    if not GOOGLE_CLIENT_ID:
        errores.append("❌ Falta GOOGLE_CLIENT_ID")
    if not GOOGLE_CLIENT_SECRET:
        errores.append("❌ Falta GOOGLE_CLIENT_SECRET")
    if not GOOGLE_REDIRECT_URI:
        errores.append("❌ Falta GOOGLE_REDIRECT_URI")

    detalles["GOOGLE_CLIENT_ID"] = GOOGLE_CLIENT_ID or "❌ No definido"
    detalles["GOOGLE_REDIRECT_URI"] = GOOGLE_REDIRECT_URI or "❌ No definido"
    detalles["URI Esperado"] = URI_ESPERADO
    detalles["Coincide con URI esperado"] = "✅ Sí" if GOOGLE_REDIRECT_URI == URI_ESPERADO else "❌ No coincide"

    url_generada = None
    estado = "⚠️ No generada"
    callback_status = "⚠️ No probado"

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

            # Verificar si la ruta de callback está activa
            try:
                ping = requests.get(URI_ESPERADO, timeout=5)
                if ping.status_code == 200:
                    callback_status = "✅ Callback activa (200 OK)"
                elif ping.status_code == 302:
                    callback_status = "🟡 Callback redirecciona (302)"
                elif ping.status_code == 404:
                    callback_status = "❌ Callback no encontrada (404)"
                else:
                    callback_status = f"⚠️ Callback responde con código {ping.status_code}"
            except Exception as e:
                callback_status = f"❌ Error al hacer ping: {str(e)}"

        except Exception as e:
            errores.append(f"❌ Error generando URL de login: {str(e)}")

    return render_template(
        "debug_google.html",
        detalles=detalles,
        errores=errores,
        auth_url=url_generada,
        estado=estado,
        callback_status=callback_status
    )
def verificar_google_login():
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        if not client_id or not client_secret or not redirect_uri:
            return {
                "version": "N/A",
                "estado": "❌ Faltan variables de entorno"
            }

        return {
            "version": "Detectado",
            "estado": "✅ Configurado correctamente"
        }
    except Exception as e:
        return {
            "version": "Error",
            "estado": f"❌ Error: {str(e)}"
        }
