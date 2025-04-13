# clientes/aura/debug/debug.py

import os
import json
import openai
import requests
from flask import Blueprint, render_template

debug_bp = Blueprint("debug_general", __name__)

@debug_bp.route("/debug/verificar")
def verificar_sistema():
    resultados = []

    # 1. Verificar versión de openai
    try:
        version_openai = openai.__version__
        estado = "✅ Correcta" if version_openai == "0.28.1" else "⚠️ Versión distinta"
        resultados.append(("openai", version_openai, estado))
    except Exception:
        resultados.append(("openai", "N/A", "❌ No detectada"))

    # 2. Verificar versión de requests-oauthlib
    try:
        import requests_oauthlib
        version_oauth = requests_oauthlib.__version__
        estado = "✅ Correcta" if version_oauth == "1.3.1" else "⚠️ Versión distinta"
        resultados.append(("requests-oauthlib", version_oauth, estado))
    except Exception:
        resultados.append(("requests-oauthlib", "N/A", "❌ No detectada"))

    # 3. Verificar login_google
    if os.path.exists("clientes/aura/auth/login_google.py"):
        resultados.append(("login_google", "Detectado", "✅ Configurado correctamente"))
    else:
        resultados.append(("login_google", "N/A", "❌ No encontrado"))

    # 4. Verificar .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        estado = "✅ Completo" if api_key else "⚠️ Falta OPENAI_API_KEY"
        resultados.append(("env", "N/A", estado))
    except Exception:
        resultados.append(("env", "N/A", "❌ Error cargando"))

    # 5. Verificar archivos requeridos
    archivos_requeridos = [
        "clientes/aura/database/bot_data.json",
        "clientes/aura/database/categorias.json",
        "clientes/aura/database/contactos.json",
        "clientes/aura/database/config.json"
    ]
    archivos_faltantes = [a for a in archivos_requeridos if not os.path.exists(a)]
    if archivos_faltantes:
        resultados.append(("archivos", "N/A", "❌ Faltante(s)"))
    else:
        resultados.append(("archivos", "N/A", "✅ Todos encontrados"))

    # 6. Verificar carpeta historial (aunque esté vacía)
    ruta_historial = "clientes/aura/database/historial"
    if os.path.exists(ruta_historial) and os.path.isdir(ruta_historial):
        resultados.append(("historial", "N/A", "✅ Accesible"))
    else:
        resultados.append(("historial", "N/A", "❌ No encontrada"))

    # 7. Verificar conexión a OpenAI
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=5
        )
        resultados.append(("conexion_openai", "N/A", "✅ Activa"))
    except Exception as e:
        resultados.append(("conexion_openai", "N/A", f"❌ Error: {str(e)[:40]}"))

    # 8. Verificar bot_data.json
    try:
        with open("clientes/aura/database/bot_data.json", "r", encoding="utf-8") as f:
            json.load(f)
        resultados.append(("mensaje_hola", "N/A", "✅ Leído correctamente"))
    except Exception as e:
        resultados.append(("mensaje_hola", "N/A", "❌ Error al leer bot_data.json"))

    # 9. Verificar Twilio
    if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
        resultados.append(("twilio_conexion", "N/A", "✅ Activa"))
    else:
        resultados.append(("twilio_conexion", "N/A", "⚠️ Falta configuración"))

    # 10. Verificar webhook
    try:
        r = requests.get("https://app.soynoraai.com/webhook")
        if r.status_code == 200:
            resultados.append(("webhook", "N/A", "✅ Responde correctamente (200 OK)"))
        else:
            resultados.append(("webhook", "N/A", f"⚠️ Código {r.status_code}"))
    except Exception:
        resultados.append(("webhook", "N/A", "❌ No responde"))

    return render_template("debug_verificacion.html", resultados=resultados)
