import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def manejar_respuesta_ai(mensaje_usuario, prompt=None):
    """
    Genera una respuesta utilizando OpenAI GPT-3.5-turbo basada en el mensaje del usuario y un prompt opcional.

    Args:
        mensaje_usuario (str): Mensaje enviado por el usuario.
        prompt (str, optional): Contexto adicional para la IA. Si no se proporciona, se usa el mensaje del usuario.

    Returns:
        str: Respuesta generada por la IA.
    """
    try:
        # Construir el mensaje para la IA
        messages = [{"role": "user", "content": prompt or mensaje_usuario}]

        # Llamar a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        # Retornar la respuesta generada
        return response.choices[0].message.content.strip()

    except openai.error.OpenAIError as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. Por favor, intenta nuevamente."
    except Exception as e:
        registrar_error("IA", f"Error inesperado al generar respuesta: {e}")
        return "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente."
