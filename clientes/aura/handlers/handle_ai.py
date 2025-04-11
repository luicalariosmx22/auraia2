import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def manejar_respuesta_ai(mensaje):
    if not os.getenv("USAR_OPENAI", "true").lower() == "true":
        return None

    try:
        prompt_base = "Responde de forma clara y profesional como si fueras un asistente de marketing. "
        prompt = prompt_base + f"Usuario: {mensaje}\nAsistente:"

        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        registrar_error("OpenAI", f"Error al generar respuesta: {e}")
        return None
