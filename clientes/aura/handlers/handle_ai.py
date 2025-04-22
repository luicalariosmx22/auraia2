import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error
from clientes.aura.utils.chat.buscar_conocimiento import obtener_base_conocimiento
from clientes.aura.utils.supabase import supabase

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def obtener_prompt_personalizado(numero_nora):
    """
    Obtiene un prompt personalizado desde Supabase basado en el numero_nora.
    """
    try:
        resultado = supabase.table("configuracion_bot").select("personalidad, instrucciones").eq("numero_nora", numero_nora).execute()
        if resultado.data:
            personalidad = resultado.data[0].get("personalidad", "")
            instrucciones = resultado.data[0].get("instrucciones", "")
            return f"{personalidad}\n\n{instrucciones}"
        print(f"⚠️ No se encontró un prompt personalizado para el número: {numero_nora}")
        return None
    except Exception as e:
        registrar_error("IA", f"No se pudo cargar el prompt personalizado: {e}")
        return None

from typing import List, Optional, Tuple, Union

def manejar_respuesta_ai(
    mensaje_usuario: str,
    numero_nora: Optional[str] = None,
    historial: Optional[List[dict]] = None,
    prompt: Optional[str] = None,
    base_conocimiento: Optional[List[dict]] = None
) -> Tuple[str, List[dict]]:
    """
    Genera una respuesta utilizando OpenAI GPT-3.5-turbo basada en el mensaje del usuario,
    un historial opcional, un prompt y una base de conocimiento. Si no se proporciona, lo obtiene por numero_nora.
    """
    try:
        # Obtener numero_nora desde Supabase si no se proporciona
        if numero_nora is None:
            try:
                resultado = supabase.table("configuracion_bot").select("numero_nora").limit(1).execute()
                if resultado.data:
                    numero_nora = resultado.data[0].get("numero_nora", "5215593372311")
                else:
                    print("⚠️ No se encontró un número de Nora en la configuración. Usando valor predeterminado.")
                    numero_nora = "5215593372311"
            except Exception as e:
                registrar_error("IA", f"No se pudo obtener el número de Nora desde Supabase: {e}")
                numero_nora = "5215593372311"
    except Exception as e:
        registrar_error("IA", f"Error inesperado al manejar el número de Nora: {e}")
        numero_nora = "5215593372311"
    try:
        # Si no se recibe la base de conocimiento, obtenerla desde Supabase
        if base_conocimiento is None:
            base_conocimiento = obtener_base_conocimiento(numero_nora)
            print(f"🔍 Base de conocimiento obtenida: {len(base_conocimiento)} registros.")

        # Inicializar el historial si no se proporciona
        if historial is None:
            historial = []

        # Si no hay historial y no se proporcionó un prompt, obtener uno desde Supabase
        if not historial:
            if not prompt:
                prompt = obtener_prompt_personalizado(numero_nora)
            if not prompt:
                prompt = (
                    "Eres un asistente virtual llamado Nora. "
                    "Tu objetivo es ayudar a los usuarios con sus preguntas de manera profesional y amigable. "
                    "Evita repetir saludos innecesarios y responde directamente a las preguntas."
                )
            historial.append({"role": "system", "content": prompt})

        # Agregar el mensaje del usuario al historial
        historial.append({"role": "user", "content": mensaje_usuario})

        # Construir el contexto para la IA
        messages = []
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
