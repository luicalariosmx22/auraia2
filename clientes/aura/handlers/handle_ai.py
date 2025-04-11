import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

RUTA_BASE_CONOCIMIENTO = "clientes/aura/config/servicios_conocimiento.txt"

def cargar_base_conocimiento():
    try:
        with open(RUTA_BASE_CONOCIMIENTO, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        registrar_error("IA", f"No se pudo cargar el archivo de conocimiento: {e}")
        return ""

def manejar_respuesta_ai(mensaje_usuario):
    usar_ia = os.getenv("USAR_OPENAI", "true").lower() == "true"
    if not usar_ia:
        return None

    try:
        conocimiento_base = cargar_base_conocimiento()

        prompt = f"""
Eres una asistente virtual llamada Nora AI, que trabaja para una agencia llamada Aura Marketing.

Tu trabajo es responder de forma clara, útil, profesional y con un toque cálido y humano. No inventes respuestas.

Usa esta información como base de conocimiento:

{conocimiento_base}

Pregunta del usuario: {mensaje_usuario}

Respuesta:
        """

        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return None
