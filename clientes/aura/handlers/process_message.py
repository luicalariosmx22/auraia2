# 📁 clientes/aura/handlers/process_message.py

from datetime import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.limpieza import limpiar_mensaje
from clientes.aura.utils.historial import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
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
    Procesa el mensaje recibido, limpia el texto, normaliza el número, obtiene historial y llama a la IA.
    """
    numero_usuario = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")
    nombre_nora = data.get("NombreNora", "nora").lower()

    # Configuración y número real de Nora
    config = obtener_config_nora(nombre_nora)
    numero_nora = config.get("numero_nora", "5210000000000")
    print(f"🔧 Configuración para {nombre_nora} → número_nora={numero_nora}")

    # Verificar si es la primera interacción
    historial = supabase.table("historial_conversaciones") \
        .select("id") \
        .eq("telefono", numero_usuario) \
        .limit(1) \
        .execute().data

    if not historial:
        mensaje_bienvenida = config.get("mensaje_bienvenida", "").strip()
        if mensaje_bienvenida:
            print("📩 Enviando mensaje de bienvenida visible...")
            enviar_mensaje(numero_usuario, mensaje_bienvenida, nombre_usuario)
            guardar_en_historial(
                telefono=numero_usuario,
                mensaje=mensaje_bienvenida,
                origen=numero_nora,
                nombre_nora=nombre_nora,
                tipo="respuesta"
            )

    # Guardar mensaje entrante en historial
    guardar_en_historial(
        telefono=numero_usuario,
        mensaje=mensaje_usuario,
        origen=numero_usuario,
        nombre_nora=nombre_nora,
        tipo="usuario"
    )

    # Generar respuesta desde IA con historial y contexto automáticamente manejados dentro de handle_ai
    respuesta, historial = manejar_respuesta_ai(
        mensaje_usuario=mensaje_usuario,
        numero_nora=numero_nora
    )

    if not respuesta:
        print("⚠️ No se pudo generar una respuesta. Usando mensaje predeterminado.")
        respuesta = "Lo siento, no puedo responder en este momento. Por favor, intenta más tarde."

    # Guardar respuesta en historial
    guardar_en_historial(
        telefono=numero_usuario,
        mensaje=respuesta,
        origen=numero_nora,
        nombre_nora=nombre_nora,
        tipo="respuesta"
    )

    # Enviar respuesta al usuario
    enviar_mensaje(numero_usuario, respuesta, nombre_usuario)
    return respuesta
