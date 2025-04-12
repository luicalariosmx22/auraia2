# clientes/aura/routes/debug_env.py

from flask import Blueprint, render_template
import os

debug_env_bp = Blueprint("debug_env", __name__)

@debug_env_bp.route("/debug/env", methods=["GET"])
def mostrar_entorno():
    claves_criticas = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "TWILIO_WHATSAPP_NUMBER",
        "OPENAI_API_KEY",
        "SECRET_KEY",
        "ADMIN_EMAILS"
    ]

    resultado = {}
    for clave in claves_criticas:
        valor = os.getenv(clave)
        resultado[clave] = "✅ OK" if valor else "❌ FALTANTE"

    # Obtener y dividir ADMIN_EMAILS si está presente
    admin_correos = []
    admin_raw = os.getenv("ADMIN_EMAILS")
    if admin_raw:
        admin_correos = [correo.strip() for correo in admin_raw.split(",")]

    return render_template("debug_env.html", resultado=resultado, admin_correos=admin_correos)
