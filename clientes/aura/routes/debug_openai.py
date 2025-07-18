# 📁 Archivo: clientes/aura/routes/debug_openai.py

from flask import Blueprint, request
import openai
import os
import pkg_resources
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

debug_openai_bp = Blueprint("debug_openai", __name__)

# Ruta de prueba manual desde navegador
@debug_openai_bp.route("/debug/openai", methods=["GET"])
def test_openai():
    try:
        prompt = request.args.get("q", "¿Qué es marketing digital?")

        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=100
        )

        output = respuesta.choices[0].message.content.strip()
        return f"<h3>✅ Respuesta OpenAI</h3><pre>{output}</pre>"

    except Exception as e:
        return f"<h3>❌ Error al conectar con OpenAI</h3><pre>{e}</pre>"

# Función auxiliar para debug_verificar.py
def verificar_openai():
    try:
        version = pkg_resources.get_distribution("openai").version
        if version == "0.28.1":
            estado = "✅ Correcta"
        else:
            estado = f"❌ Incorrecta (usa 0.28.1)"

        return {
            "version": version,
            "estado": estado
        }
    except Exception as e:
        return {
            "version": None,
            "estado": f"❌ No instalada ({str(e)})"
        }
