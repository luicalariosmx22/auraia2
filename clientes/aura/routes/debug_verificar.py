# 📁 Archivo: clientes/aura/routes/debug_verificar.py

from flask import Blueprint, render_template, jsonify
import os
import openai
from dotenv import load_dotenv
import json
import pkg_resources

from clientes.aura.routes.debug_openai import verificar_openai
from clientes.aura.routes.debug_oauthlib import verificar_oauthlib
from clientes.aura.routes.debug_google import verificar_google_login

debug_verificar_bp = Blueprint("debug_verificar", __name__)
load_dotenv()


def generar_resultado_verificacion():
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

    # Archivos clave
    archivos = {
        "bot_data.json": os.path.exists("bot_data.json"),
        "servicios_conocimiento.txt": os.path.exists("servicios_conocimiento.txt")
    }
    resultado["archivos"] = {
        "version": None,
        "estado": "✅ OK" if all(archivos.values()) else "❌ Faltante(s)"
    }

    # Historial
    historial_path = "clientes/aura/database/historial"
    resultado["historial"] = {
        "version": None,
        "estado": "✅ Accesible" if os.path.isdir(historial_path) else "❌ No encontrada"
    }

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

    # Verificación de palabra clave "hola" en bot_data.json
    try:
        with open("bot_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        hay_hola = any(item.get("keyword") == "hola" for item in data)
        resultado["mensaje_hola"] = {
            "version": None,
            "estado": "✅ Existe" if hay_hola else "❌ No configurado"
        }
    except:
        resultado["mensaje_hola"] = {
            "version": None,
            "estado": "❌ Error al leer bot_data.json"
        }

    return resultado


# 🧪 Ruta visual con tabla en HTML
@debug_verificar_bp.route("/debug/verificacion", methods=["GET"])
def vista_verificacion():
    resultado = generar_resultado_verificacion()
    return render_template("debug_verificacion.html", resultado=resultado)


# 📡 Ruta JSON para JS (fetch en HTML)
@debug_verificar_bp.route("/debug/verificar", methods=["GET"])
def api_verificacion():
    resultado = generar_resultado_verificacion()
    return jsonify(resultado)
