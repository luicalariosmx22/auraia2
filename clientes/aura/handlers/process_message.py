# 📁 clientes/aura/handlers/process_message.py

import os  # Asegúrate de importar os si no está ya importado
from datetime import datetime  # ✅ Importación necesaria
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.limpieza import limpiar_mensaje
from clientes.aura.utils.history import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.utils.settings_loader import cargar_settings
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.handlers.handle_files import manejar_archivos_adjuntos
from clientes.aura.utils.comunicacion_contextual import debe_saludar, debe_preguntar_si_hay_duda

# ✅ Importar desde Supabase
from utils.db.contactos import obtener_contacto
from clientes.aura.utils.buscar_conocimiento import buscar_conocimiento
from clientes.aura.utils.supabase import supabase  # ✅ Importación agregada

# Función para obtener configuración de Nora
def obtener_config_nora(nombre_nora):
    """
    Obtiene la configuración de Nora. Si es la Nora base ('nora'), devuelve una configuración predeterminada.
    Para otras Noras, consulta la tabla 'configuracion_bot' en Supabase.
    """
    # Normalizar el nombre de Nora a minúsculas
    nombre_nora = nombre_nora.lower()

    if nombre_nora == "nora":
        # Configuración predeterminada para la Nora base
        print("🔧 Cargando configuración predeterminada para la Nora base.")
        return {
            "nombre_nora": "nora",
            "numero_nora": os.getenv("NORA_NUMERO", "5210000000000"),  # Número de Nora desde las variables de entorno
            "modulos": ["ia", "conocimiento", "panel_admin"]  # Módulos predeterminados
        }

    # Consultar configuración en Supabase para otras Noras
    try:
        print(f"🔍 Buscando configuración para Nora del cliente: {nombre_nora}")
        response = (
            supabase.table("configuracion_bot")
            .select("*")
            .eq("nombre_nora", nombre_nora)
            .execute()
        )
        data = response.data or []

        if not data:
            print(f"⚠️ No se encontró configuración para Nora del cliente: {nombre_nora}")
            return {}

        print(f"✅ Configuración encontrada para Nora del cliente: {data[0]}")
        return data[0]
    except Exception as e:
        print(f"❌ Error al obtener configuración de Nora ({nombre_nora}): {e}")
        return {}

def procesar_mensaje(data):
    # Obtener datos del mensaje
    numero = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")  # ✅ Obtener el ProfileName del usuario
    nombre_nora = data.get("NombreNora", "nora").lower()  # ✅ Normalizar el nombre de Nora a minúsculas

    # Obtener configuración de Nora
    config = obtener_config_nora(nombre_nora)
    nora_numero = config.get("numero_nora", "5210000000000")  # Número por defecto si algo falla
    print(f"🔧 Configuración de Nora ({nombre_nora}):", config)
    print(f"📞 Número de Nora: {nora_numero}")

    # Guardar mensaje del usuario en el historial
    guardar_en_historial(
        numero,
        mensaje_usuario,
        "recibido",
        nombre_nora
    )

    # Consultar la base de conocimiento en Supabase
    response = (
        supabase.table("base_conocimiento")
        .select("pregunta,respuesta")
        .eq("nombre_nora", nombre_nora)
        .execute()
    )

    # Buscar conocimiento en la base de datos
    print(f"📚 Buscando en base de conocimiento para '{mensaje_usuario}' en Nora: '{nombre_nora}'...")
    respuesta_conocimiento = buscar_conocimiento(nombre_nora, mensaje_usuario)

    if respuesta_conocimiento:
        print(f"✅ ¡Conocimiento encontrado!: {respuesta_conocimiento}")
        # Guardar respuesta del bot en el historial
        guardar_en_historial(
            nora_numero,
            respuesta_conocimiento,
            "enviado",
            nombre_nora
        )

        # Enviar respuesta al usuario usando nombre_usuario
        enviar_mensaje(numero, respuesta_conocimiento, nombre_usuario)  # ✅ Usar nombre_usuario
        return respuesta_conocimiento
    else:
        print("❌ No se encontró conocimiento. Pasando a IA...")

    # Si no se encuentra conocimiento, usar IA
    respuesta_ia = manejar_respuesta_ai(mensaje_usuario)

    # Guardar respuesta generada por la IA en el historial
    guardar_en_historial(
        nora_numero,
        respuesta_ia,
        "enviado",
        nombre_nora
    )

    # Enviar respuesta al usuario usando nombre_usuario
    enviar_mensaje(numero, respuesta_ia, nombre_usuario)  # ✅ Usar nombre_usuario
    return respuesta_ia
