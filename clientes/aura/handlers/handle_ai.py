import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def manejar_respuesta_ai(mensaje_usuario, historial=None, prompt=None):
    """
    Genera una respuesta utilizando OpenAI GPT-3.5-turbo basada en el mensaje del usuario y un historial opcional.
    """
    try:
        # Inicializar el historial si no se proporciona
        if historial is None:
            historial = []

        # Agregar un prompt inicial si el historial está vacío
        if not historial:
            prompt_inicial = (
                "Eres un asistente virtual llamado Nora. "
                "Tu objetivo es ayudar a los usuarios con sus preguntas de manera profesional y amigable. "
                "Evita repetir saludos innecesarios y responde directamente a las preguntas."
            )
            historial.append({"role": "system", "content": prompt_inicial})

        # Agregar el mensaje del usuario al historial
        historial.append({"role": "user", "content": mensaje_usuario})

        # Construir el contexto para la IA
        messages = [{"role": "system", "content": prompt}] if prompt else []
        messages.extend(historial)

        # Llamar a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )

        # Obtener la respuesta generada
        respuesta = response.choices[0].message.content.strip()

        # Agregar la respuesta de la IA al historial
        historial.append({"role": "assistant", "content": respuesta})

        return respuesta, historial

    except openai.error.OpenAIError as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. Por favor, intenta nuevamente.", historial
    except Exception as e:
        registrar_error("IA", f"Error inesperado al generar respuesta: {e}")
        return "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente.", historial
