# ✅ ARCHIVO: clientes/aura/handlers/handle_ai.py

import os
import openai
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from clientes.aura.utils.error_logger import registrar_error
from clientes.aura.utils.chat.buscar_conocimiento import obtener_base_conocimiento
from clientes.aura.utils.supabase import supabase

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def obtener_prompt_personalizado(numero_nora: str) -> Optional[str]:
    """
    Obtiene el prompt personalizado desde la base de datos para un número específico.
    """
    try:
        resultado = (
            supabase
            .table("configuracion_bot")
            .select("personalidad, instrucciones")
            .eq("numero_nora", numero_nora)
            .single()
            .execute()
        )

        if resultado.data:
            personalidad = resultado.data.get("personalidad", "").strip()
            instrucciones = resultado.data.get("instrucciones", "").strip()

            # Verificar si personalidad e instrucciones están definidas
            if not personalidad:
                print("⚠️ La personalidad no está definida. Usando valor por defecto: 'profesional y amigable'.")
                personalidad = "profesional y amigable"

            if not instrucciones:
                print("⚠️ Las instrucciones no están definidas. Usando valor por defecto: 'Responde de forma clara y útil.'")
                instrucciones = "Responde de forma clara y útil."

            prompt = f"{personalidad}\n\n{instrucciones}"
            print(f"✅ Prompt personalizado generado: {prompt}")
            return prompt

        print(f"⚠️ No se encontró un prompt personalizado para el número: {numero_nora}")
        return None

    except Exception as e:
        registrar_error("IA", f"No se pudo cargar el prompt personalizado: {e}")
        return None


def manejar_respuesta_ai(
    mensaje_usuario: str,
    numero_nora: Optional[str] = None,
    historial: Optional[List[dict]] = None,
    prompt: Optional[str] = None,
    base_conocimiento: Optional[List[dict]] = None
) -> Tuple[str, List[dict]]:
    """
    Genera una respuesta utilizando OpenAI GPT-3.5-turbo basada en el mensaje del usuario.
    """
    try:
        if numero_nora is None:
            resultado = supabase.table("configuracion_bot").select("numero_nora").limit(1).execute()
            if resultado.data:
                numero_nora = resultado.data[0].get("numero_nora", "5215593372311")
            else:
                numero_nora = "5215593372311"
                print("⚠️ No se encontró número_nora. Usando valor por defecto.")

        if base_conocimiento is None:
            base_conocimiento = obtener_base_conocimiento(numero_nora)
            print(f"🔍 Base de conocimiento obtenida: {len(base_conocimiento)} bloques.")

        if historial is None:
            historial = []

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

        historial.append({"role": "user", "content": mensaje_usuario})

        messages = []
        if base_conocimiento:
            for item in base_conocimiento:
                messages.append({"role": "system", "content": item["contenido"]})
        messages.extend(historial)

        print(f"📜 Contexto construido para OpenAI: {messages}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )

        respuesta = response.choices[0].message.content.strip()
        print(f"✅ Respuesta generada por OpenAI: {respuesta}")
        historial.append({"role": "assistant", "content": respuesta})
        return respuesta, historial

    except openai.error.OpenAIError as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. Por favor, intenta nuevamente.", historial

    except Exception as e:
        registrar_error("IA", f"Error inesperado al generar respuesta: {e}")
        return "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente.", historial
