import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error
from clientes.aura.utils.chat.buscar_conocimiento import obtener_base_conocimiento  # 🆕

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def manejar_respuesta_ai(mensaje_usuario, nombre_nora="aura", historial=None, prompt=None, base_conocimiento=None):
    """
    Genera una respuesta utilizando OpenAI GPT-3.5-turbo basada en el mensaje del usuario,
    un historial opcional, un prompt y una base de conocimiento. Si no se proporciona, lo obtiene por nombre_nora.
    """
    try:
        # Si no se recibe la base de conocimiento, obtenerla desde Supabase
        if base_conocimiento is None:
            base_conocimiento = obtener_base_conocimiento(nombre_nora)
            print(f"🔍 Base de conocimiento obtenida: {len(base_conocimiento)} registros.")

        # Inicializar el historial si no se proporciona
        if historial is None:
            historial = []

        # Si no hay historial ni prompt, usar un prompt predeterminado
        if not historial and not prompt:
            print("⚠️ No se encontró historial ni prompt. Usando prompt predeterminado.")
            prompt = (
                "Eres un asistente virtual llamado Nora. "
                "Tu objetivo es ayudar a los usuarios con sus preguntas de manera profesional y amigable. "
                "Evita repetir saludos innecesarios y responde directamente a las preguntas."
            )

        # Agregar el prompt inicial al historial si no existe
        if not historial:
            historial.append({"role": "system", "content": prompt})

        # Agregar el mensaje del usuario al historial
        historial.append({"role": "user", "content": mensaje_usuario})

        # Construir el contexto para la IA
        messages = [{"role": "system", "content": prompt}] if prompt else []
        if base_conocimiento:
            for item in base_conocimiento:
                messages.append({"role": "system", "content": item["contenido"]})
        messages.extend(historial)

        print(f"📜 Contexto construido para OpenAI: {messages}")

        # Llamar a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )

        # Obtener la respuesta generada
        respuesta = response.choices[0].message.content.strip()
        print(f"✅ Respuesta generada por OpenAI: {respuesta}")

        # Agregar la respuesta de la IA al historial
        historial.append({"role": "assistant", "content": respuesta})

        return respuesta, historial

    except openai.error.OpenAIError as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. Por favor, intenta nuevamente.", historial
    except Exception as e:
        registrar_error("IA", f"Error inesperado al generar respuesta: {e}")
        return "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente.", historial
