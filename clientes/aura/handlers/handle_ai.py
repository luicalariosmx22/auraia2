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

def obtener_configuracion_nora(nombre_nora: str) -> Tuple[str, str, str, str]:
    """
    Obtiene la configuración completa desde la base de datos para un número específico.
    Retorna personalidad, instrucciones, modo_respuesta y mensaje_fuera_tema.
    """
    try:
        print(f"🔍 Buscando configuración para Nora: {nombre_nora}")
        resultado = (
            supabase
            .table("configuracion_bot")
            .select("personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema")
            .eq("nombre_nora", nombre_nora)
            .limit(1)
            .execute()
        )
        if resultado.data:
            datos = resultado.data[0]
            print(f"✅ Configuración encontrada para {nombre_nora}")
            personalidad = datos.get("personalidad", "profesional y amigable").strip()
            instrucciones = datos.get("instrucciones", "Responde de forma clara y útil.").strip()
            modo_respuesta = datos.get("modo_respuesta", "flexible")
            mensaje_fuera_tema = datos.get("mensaje_fuera_tema", 
                "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor.")
            return personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema
        else:
            print(f"⚠️ No se encontró configuración para {nombre_nora}, usando valores por defecto")
        return "profesional y amigable", "Responde de forma clara y útil.", "flexible", \
               "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor."
    except Exception as e:
        print(f"❌ Error al obtener configuración de Nora: {e}")
        registrar_error("IA", f"No se pudo cargar configuración de Nora: {e}")
        return "profesional y amigable", "Responde de forma clara y útil.", "flexible", \
               "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor."

def construir_prompt(personalidad: str, instrucciones: str, modo_respuesta: str = "flexible", tipo_contacto: dict = None) -> str:
    prompt_base = f"{personalidad}\n\n{instrucciones}"
    
    # 🆕 Agregar información del tipo de contacto al prompt
    if tipo_contacto:
        if tipo_contacto["tipo"] == "usuario_cliente":
            rol = tipo_contacto.get("rol", "empleado")
            prompt_base += f"\n\nNOTA IMPORTANTE: Estás hablando con {tipo_contacto['nombre']}, quien es un USUARIO INTERNO ({rol}) de nuestro equipo."
            
            # Verificar si es supervisor o admin
            if tipo_contacto.get("es_supervisor") or tipo_contacto.get("rol") == "interno":
                prompt_base += f"\n🔑 ACCESO PRIVILEGIADO: Esta persona tiene permisos de supervisión. Puedes proporcionar información interna, estadísticas detalladas y acceso a funciones administrativas."
            
            prompt_base += f"\n\nPuedes responder cualquier pregunta relacionada con el trabajo, proyectos, tareas, o información interna de la empresa. Sé profesional y directo."
            
        elif tipo_contacto["tipo"] == "cliente":
            prompt_base += f"\n\nNOTA IMPORTANTE: Estás hablando con {tipo_contacto['nombre']}, quien es un CLIENTE registrado en nuestro sistema."
            
            # 🏢 Agregar información de empresas si las tiene
            empresas = tipo_contacto.get("empresas", [])
            if empresas:
                prompt_base += f"\n\n🏢 INFORMACIÓN DE SUS EMPRESAS:"
                for empresa in empresas:
                    nombre_empresa = empresa.get('nombre_empresa', 'Sin nombre')
                    descripcion = empresa.get('descripcion', '')
                    industria = empresa.get('industria', '')
                    
                    prompt_base += f"\n- Empresa: {nombre_empresa}"
                    if industria:
                        prompt_base += f" (Industria: {industria})"
                    if descripcion:
                        prompt_base += f"\n  Descripción: {descripcion}"
                
                prompt_base += f"\n\nPuedes hacer referencia a su(s) empresa(s) y ofrecer servicios específicos para su industria. Sé personalizado y profesional."
            else:
                prompt_base += " Trata de ser más personalizado y profesional."
                
        else:
            prompt_base += "\n\nNOTA IMPORTANTE: Estás hablando con un visitante que no está registrado en nuestro sistema. Sé amable y trata de convertirlo en cliente potencial."
    
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
    nombre_nora: Optional[str] = None,
    historial: Optional[List[dict]] = None,
    prompt: Optional[str] = None,
    base_conocimiento: Optional[List[dict]] = None,
    tipo_contacto: Optional[dict] = None  # 🆕 Nuevo parámetro
) -> Tuple[str, List[dict]]:
    try:
        if nombre_nora is None:
            resultado = supabase.table("configuracion_bot").select("nombre_nora").limit(1).execute()
            nombre_nora = resultado.data[0].get("nombre_nora", "aura") if resultado.data else "aura"

        if base_conocimiento is None:
            base_conocimiento = obtener_base_conocimiento(nombre_nora)
            print(f"🔍 Base de conocimiento obtenida: {len(base_conocimiento)} bloques.")

        if historial is None:
            historial = []

        # Obtener configuración completa de Nora
        personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema = obtener_configuracion_nora(nombre_nora)
        print(f"⚙️ Configuración Nora - Modo: {modo_respuesta}")

        # Si el contacto NO es cliente ni usuario_cliente, aplicar modo estricto
        if modo_respuesta == "estricto" and not (tipo_contacto and tipo_contacto.get("tipo") in ["cliente", "usuario_cliente"]):
            es_relevante = verificar_relevancia_pregunta(mensaje_usuario, base_conocimiento)
            if not es_relevante:
                print(f"🚫 Pregunta fuera del área de conocimiento en modo estricto")
                historial.append({"role": "user", "content": mensaje_usuario})
                historial.append({"role": "assistant", "content": mensaje_fuera_tema})
                return mensaje_fuera_tema, historial
        elif tipo_contacto and tipo_contacto.get("tipo") == "usuario_cliente":
            print(f"🔓 Modo estricto DESHABILITADO para usuario interno: {tipo_contacto.get('nombre')}")
        elif tipo_contacto and tipo_contacto.get("tipo") == "cliente":
            print(f"🔓 Modo estricto DESHABILITADO para cliente: {tipo_contacto.get('nombre')}")
        else:
            print(f"⚠️ Visitante desconocido - aplicando modo estricto")

        if not any(msg["role"] == "system" for msg in historial):
            prompt = construir_prompt(personalidad, instrucciones, modo_respuesta, tipo_contacto)  # 🆕 Pasar tipo_contacto
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
