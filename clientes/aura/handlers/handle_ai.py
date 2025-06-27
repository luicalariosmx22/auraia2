# ✅ ARCHIVO: clientes/aura/handlers/handle_ai.py

import os
import openai
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from clientes.aura.utils.error_logger import registrar_error
from clientes.aura.utils.chat.buscar_conocimiento import obtener_base_conocimiento
from clientes.aura.utils.supabase_client import supabase

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def obtener_configuracion_nora(numero_nora: str) -> Tuple[str, str, str, str]:
    """
    Obtiene la configuración completa desde la base de datos para un número específico.
    Retorna personalidad, instrucciones, modo_respuesta y mensaje_fuera_tema.
    """
    try:
        resultado = (
            supabase
            .table("configuracion_bot")
            .select("personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema")
            .eq("numero_nora", numero_nora)
            .limit(1)
            .execute()
        )
        if resultado.data:
            datos = resultado.data[0]
            personalidad = datos.get("personalidad", "profesional y amigable").strip()
            instrucciones = datos.get("instrucciones", "Responde de forma clara y útil.").strip()
            modo_respuesta = datos.get("modo_respuesta", "flexible")
            mensaje_fuera_tema = datos.get("mensaje_fuera_tema", 
                "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor.")
            return personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema
        return "profesional y amigable", "Responde de forma clara y útil.", "flexible", \
               "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor."
    except Exception as e:
        registrar_error("IA", f"No se pudo cargar configuración de Nora: {e}")
        return "profesional y amigable", "Responde de forma clara y útil.", "flexible", \
               "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor."

def construir_prompt(personalidad: str, instrucciones: str, modo_respuesta: str = "flexible") -> str:
    prompt_base = f"{personalidad}\n\n{instrucciones}"
    
    if modo_respuesta == "estricto":
        prompt_restriccion = "\n\nIMPORTANTE: Solo puedes responder sobre temas relacionados con la información proporcionada en tu base de conocimiento. Si la pregunta no está relacionada con tu empresa, servicios o información que tienes disponible, debes responder exactamente con el mensaje configurado para temas fuera de tu área."
        return prompt_base + prompt_restriccion
    
    return prompt_base

def verificar_relevancia_pregunta(mensaje_usuario: str, base_conocimiento: List[dict]) -> bool:
    """
    Verifica si la pregunta del usuario está relacionada con la base de conocimiento.
    Retorna True si es relevante, False si no.
    """
    try:
        # Crear un prompt para evaluar relevancia
        conocimiento_resumido = "\n".join([item["contenido"][:200] + "..." for item in base_conocimiento[:5]])
        
        prompt_evaluacion = f"""
Analiza si la siguiente pregunta está relacionada con la información de la empresa:

INFORMACIÓN DE LA EMPRESA:
{conocimiento_resumido}

PREGUNTA DEL USUARIO: {mensaje_usuario}

Responde SOLO "SI" si la pregunta está relacionada con la empresa, sus servicios, productos o información disponible.
Responde SOLO "NO" si la pregunta es sobre temas generales, personales o no relacionados con la empresa.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_evaluacion}],
            temperature=0.1,
            max_tokens=10
        )
        
        respuesta_evaluacion = response.choices[0].message.content.strip().upper()
        print(f"🎯 Evaluación de relevancia: '{respuesta_evaluacion}' para pregunta: '{mensaje_usuario}'")
        
        return respuesta_evaluacion == "SI"
        
    except Exception as e:
        registrar_error("IA", f"Error al verificar relevancia: {e}")
        # En caso de error, permitir la pregunta (modo conservador)
        return True

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

        # Obtener configuración completa de Nora
        personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema = obtener_configuracion_nora(numero_nora)
        print(f"⚙️ Configuración Nora - Modo: {modo_respuesta}")

        # Verificar relevancia si está en modo estricto
        if modo_respuesta == "estricto":
            es_relevante = verificar_relevancia_pregunta(mensaje_usuario, base_conocimiento)
            if not es_relevante:
                print(f"🚫 Pregunta fuera del área de conocimiento en modo estricto")
                historial.append({"role": "user", "content": mensaje_usuario})
                historial.append({"role": "assistant", "content": mensaje_fuera_tema})
                return mensaje_fuera_tema, historial

        if not any(msg["role"] == "system" for msg in historial):
            prompt = construir_prompt(personalidad, instrucciones, modo_respuesta)
            historial.insert(0, {"role": "system", "content": prompt})

        historial.append({"role": "user", "content": mensaje_usuario})
        messages = construir_contexto(base_conocimiento, historial)

        print(f"📜 Contexto construido para OpenAI: {len(messages)} mensajes")

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
