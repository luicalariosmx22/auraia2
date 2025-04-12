# 📁 Archivo: clientes/aura/routes/debug_verificar.py

from flask import Blueprint, render_template, jsonify
import os
import openai
from dotenv import load_dotenv

# Auxiliares
from clientes.aura.routes.debug_openai import verificar_openai
from clientes.aura.routes.debug_oauthlib import verificar_oauthlib

debug_verificar_bp = Blueprint("debug_verificar", __name__)
load_dotenv()

# Ruta que regresa JSON para el HTML dinámico
@debug_verificar_bp.route("/debug/verificar", methods=["GET"])
def verificar_configuracion():
    resultado = {}

    # Verificar versión de OpenAI (versión y estado)
    resultado["openai"] = verificar_openai()

    # Verificar requests-oauthlib
    resultado["requests-oauthlib"] = verificar_oauthlib()

    # Verificar variables de entorno
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
        "estado": "✅ Completo" if not faltantes else f"❌ Faltan: {', '.join(faltantes)}"
    }

    # Verificar archivos clave
    archivos = {
        "bot_data.json": os.path.exists("bot_data.json"),
        "servicios_conocimiento.txt": os.path.exists("servicios_conocimiento.txt")
    }
    resultado["archivos"] = {
        nombre: "✅ OK" if existe else "❌ Faltante"
        for nombre, existe in archivos.items()
    }

    # Verificar carpeta historial
    historial_path = "clientes/aura/database/historial"
    resultado["historial"] = {
        "estado": "✅ Accesible" if os.path.isdir(historial_path) else "❌ No encontrada"
    }

    # Verificar conexión a OpenAI
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1
        )
        resultado["conexion_openai"] = {"estado": "✅ Activa"}
    except Exception as e:
        resultado["conexion_openai"] = {"estado": f"❌ Error: {str(e)}"}

    return jsonify(resultado)

# Ruta que carga la vista HTML
@debug_verificar_bp.route("/debug/verificacion", methods=["GET"])
def vista_html_verificacion():
    return render_template("debug_verificacion.html")

# DEBUG INICIAL PARA VERIFICAR QUE SE CARGÓ EL MODULO
print("✅ Módulo debug_verificar.py cargado correctamente.")
