print("✅ debug_verificar.py cargado correctamente")

from flask import Blueprint, render_template
import os
import openai
import json
import pkg_resources
from dotenv import load_dotenv
from supabase import create_client

from clientes.aura.routes.debug_openai import verificar_openai
from clientes.aura.routes.debug_oauthlib import verificar_oauthlib
from clientes.aura.routes.debug_google import verificar_google_login

debug_verificar_bp = Blueprint("debug_verificar", __name__)

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@debug_verificar_bp.route("/debug/verificar", methods=["GET"])  # ✅ RUTA CORREGIDA
def verificar_configuracion():
    resultado = {}

    # OpenAI
    resultado["openai"] = verificar_openai()

    # OAuthLib
    resultado["requests-oauthlib"] = verificar_oauthlib()

    # Google Login
    resultado["login_google"] = verificar_google_login()

    # Variables de entorno necesarias
    required_env = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "TWILIO_WHATSAPP_NUMBER",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI"
    ]
    faltantes = [var for var in required_env if not os.getenv(var)]
    resultado["env"] = {
        "version": None,
        "estado": "✅ Completo" if not faltantes else f"❌ Faltan: {', '.join(faltantes)}"
    }

    # Verificar datos en Supabase
    try:
        # Verificar tabla bot_data
        response = supabase.table("bot_data").select("*").execute()
        if response.error or not response.data:
            resultado["bot_data"] = {"estado": "❌ Faltante"}
        else:
            resultado["bot_data"] = {"estado": "✅ OK"}

        # Verificar tabla servicios_conocimiento
        response = supabase.table("servicios_conocimiento").select("*").execute()
        if response.error or not response.data:
            resultado["servicios_conocimiento"] = {"estado": "❌ Faltante"}
        else:
            resultado["servicios_conocimiento"] = {"estado": "✅ OK"}

        # Verificar tabla historial_conversaciones
        response = supabase.table("historial_conversaciones").select("*").limit(1).execute()
        if response.error or not response.data:
            resultado["historial"] = {"estado": "❌ No encontrada"}
        else:
            resultado["historial"] = {"estado": "✅ Accesible"}
    except Exception as e:
        print(f"❌ Error al verificar datos en Supabase: {str(e)}")

    # Conexión real a OpenAI
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1
        )
        resultado["conexion_openai"] = {
            "version": None,
            "estado": "✅ Activa"
        }
    except Exception as e:
        resultado["conexion_openai"] = {
            "version": None,
            "estado": f"❌ Error: {str(e)}"
        }

    # Verificar conexión real con Twilio
    try:
        from twilio.rest import Client
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        mensajes = client.messages.list(limit=1)
        resultado["twilio_conexion"] = {
            "version": None,
            "estado": "✅ Activa"
        }
    except Exception as e:
        resultado["twilio_conexion"] = {
            "version": None,
            "estado": f"❌ Error: {str(e)}"
        }

    # Verificar webhook
    try:
        import requests
        from urllib.parse import urljoin

        base_url = os.getenv("BASE_URL", "https://app.soynoraai.com/")
        webhook_url = urljoin(base_url, "/webhook")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "From": "whatsapp:+521234567890",
            "Body": "hola",
            "ProfileName": "Prueba Webhook",
            "WaId": "1234567890"
        }

        response = requests.post(webhook_url, data=payload, headers=headers)

        if response.status_code == 200:
            resultado["webhook"] = {
                "version": None,
                "estado": "✅ Responde correctamente (200 OK)"
            }
        else:
            resultado["webhook"] = {
                "version": None,
                "estado": f"⚠️ Código {response.status_code}"
            }
    except Exception as e:
        resultado["webhook"] = {
            "version": None,
            "estado": f"❌ Error: {str(e)}"
        }

    return render_template("debug_verificacion.html", resultado=resultado)
