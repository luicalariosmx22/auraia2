import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error
from clientes.aura.utils.supabase import supabase  # ✅ Necesario para traer conocimiento

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def obtener_base_conocimiento(nombre_nora):
    try:
        response = supabase.table("configuracion_bot").select("base_conocimiento").eq("nombre_nora", nombre_nora).execute()
        if response.data:
            texto = response.data[0]["base_conocimiento"]
            print(f"📚 Base de conocimiento de '{nombre_nora}' obtenida correctamente.")
            return [{"contenido": texto}]
        else:
            print(f"⚠️ No se encontró base de conocimiento para '{nombre_nora}'.")
            return []
    except Exception as e:
        print(f"❌ Error al obtener base de conocimiento para {nombre_nora}: {e}")
        return []

def manejar_respuesta_ai(mensaje_usuario, historial=None, prompt=None, base_conocimiento=None, nombre_nora=None):
    try:
        if historial is None:
            historial = []

        if not historial:
            prompt_inicial = (
                "Eres un asistente virtual llamado Nora. "
                "Tu objetivo es ayudar a los usuarios con sus preguntas de manera profesional y amigable. "
                "Evita repetir saludos innecesarios y responde directamente a las preguntas."
            )
            historial.append({"role": "system", "content": prompt_inicial})

        historial.append({"role": "user", "content": mensaje_usuario})

        messages = [{"role": "system", "content": prompt}] if prompt else []

        if base_conocimiento is None and nombre_nora:
            base_conocimiento = obtener_base_conocimiento(nombre_nora)

        if base_conocimiento:
            for item in base_conocimiento:
                messages.append({"role": "system", "content": item["contenido"]})

        messages.extend(historial)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )

        respuesta = response.choices[0].message.content.strip()
        historial.append({"role": "assistant", "content": respuesta})

        return respuesta, historial

    except openai.error.OpenAIError as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. Por favor, intenta nuevamente.", historial
    except Exception as e:
        registrar_error("IA", f"Error inesperado al generar respuesta: {e}")
        return "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente.", historial
