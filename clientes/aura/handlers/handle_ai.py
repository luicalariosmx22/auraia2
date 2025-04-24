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

def obtener_personalidad(numero_nora: str) -> Tuple[str, str]:
    """
    Obtiene la personalidad e instrucciones desde la base de datos para un número específico.
    Retorna ambos valores como strings.
    """
    try:
        resultado = (
            supabase
            .table("configuracion_bot")
            .select("personalidad, instrucciones")
            .eq("numero_nora", numero_nora)
            .limit(1)
            .execute()
        )
        if resultado.data:
            datos = resultado.data[0]
            personalidad = datos.get("personalidad", "profesional y amigable").strip()
            instrucciones = datos.get("instrucciones", "Responde de forma clara y útil.").strip()
            return personalidad, instrucciones
        return "profesional y amigable", "Responde de forma clara y útil."
    except Exception as e:
        registrar_error("IA", f"No se pudo cargar personalidad e instrucciones: {e}")
        return "profesional y amigable", "Responde de forma clara y útil."

def construir_prompt(personalidad: str, instrucciones: str) -> str:
    return f"{personalidad}\n\n{instrucciones}"

def construir_contexto(base_conocimiento: List[dict], historial: List[dict]) -> List[dict]:
    contexto = []
    for item in base_conocimiento:
        contexto.append({"role": "system", "content": item["contenido"]})
    contexto.extend(historial)
    return contexto

def manejar_respuesta_ai(
    mensaje_usuario: str,
    numero_nora: Optional[str] = None,
    historial: Optional[List[dict]] = None,
    prompt: Optional[str] = None,
    base_conocimiento: Optional[List[dict]] = None
) -> Tuple[str, List[dict]]:
    try:
        if numero_nora is None:
            resultado = supabase.table("configuracion_bot").select("numero_nora").limit(1).execute()
            numero_nora = resultado.data[0].get("numero_nora", "5215593372311") if resultado.data else "5215593372311"

        if base_conocimiento is None:
            base_conocimiento = obtener_base_conocimiento(numero_nora)
            print(f"🔍 Base de conocimiento obtenida: {len(base_conocimiento)} bloques.")

        if historial is None:
            historial = []

        if not any(msg["role"] == "system" for msg in historial):
            personalidad, instrucciones = obtener_personalidad(numero_nora)
            prompt = construir_prompt(personalidad, instrucciones)
            historial.insert(0, {"role": "system", "content": prompt})

        historial.append({"role": "user", "content": mensaje_usuario})
        messages = construir_contexto(base_conocimiento, historial)

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
