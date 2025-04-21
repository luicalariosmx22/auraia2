# 📁 clientes/aura/handlers/process_message.py

from datetime import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.limpieza import limpiar_mensaje
from clientes.aura.utils.history import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.utils.settings_loader import cargar_settings
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.utils.comunicacion_contextual import debe_saludar, debe_preguntar_si_hay_duda

from utils.db.contactos import obtener_contacto
from clientes.aura.utils.buscar_conocimiento import buscar_conocimiento
from clientes.aura.utils.supabase import supabase

def obtener_config_nora(nombre_nora):
    """
    Obtiene la configuración de Nora desde Supabase.
    """
    try:
        response = supabase.table("configuracion_bot") \
            .select("*") \
            .eq("nombre_nora", nombre_nora.lower()) \
            .execute()
        data = response.data
        return data[0] if data else {}
    except Exception as e:
        print(f"❌ Error al obtener configuración: {e}")
        return {}

def procesar_mensaje(data):
    """
    Procesa el mensaje recibido, busca en la memoria extendida y utiliza IA para generar una respuesta.
    """
    # Obtener datos del mensaje
    numero_usuario = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")
    nombre_nora = data.get("NombreNora", "nora").lower()

    # Configuración de la Nora
    config = obtener_config_nora(nombre_nora)
    numero_nora = config.get("numero_nora", "5210000000000")
    print(f"🔧 Configuración para {nombre_nora} → número_nora={numero_nora}")

    # Guardar el mensaje del usuario en el historial
    guardar_en_historial(
        numero_usuario,
        mensaje_usuario,
        origen=numero_usuario,
        nombre_nora=nombre_nora,
        tipo="usuario"
    )

    # 🧠 Buscar en la memoria extendida (base de conocimiento)
    prompt_conocimiento = buscar_conocimiento(numero_nora, mensaje_usuario)

    if prompt_conocimiento:
        print("📖 Usando memoria como contexto")
        respuesta = manejar_respuesta_ai(mensaje_usuario, prompt=prompt_conocimiento)
    else:
        print("🧠 Usando IA sin contexto")
        respuesta = manejar_respuesta_ai(mensaje_usuario)

    # Guardar la respuesta generada en el historial
    guardar_en_historial(
        numero_usuario,
        respuesta,
        origen=numero_nora,
        nombre_nora=nombre_nora,
        tipo="respuesta"
    )

    # Enviar respuesta al usuario
    enviar_mensaje(numero_usuario, respuesta, nombre_usuario)
    return respuesta
