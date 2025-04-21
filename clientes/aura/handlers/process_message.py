# 📁 clientes/aura/handlers/process_message.py

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
    response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).single().execute()
    return response.data if response.data else {}

def procesar_mensaje(data):
    # Obtener datos del mensaje
    numero = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")
    nombre_nora = data.get("NombreNora", "Nora")  # ✅ Dinámico: Obtener el nombre de Nora desde los datos

    # Obtener configuración de Nora
    config = obtener_config_nora(nombre_nora)
    nora_numero = config.get("numero_nora", "5210000000000")  # Número por defecto si algo falla
    print(f"🔧 Configuración de Nora ({nombre_nora}):", config)
    print(f"📞 Número de Nora: {nora_numero}")

    # Guardar mensaje del usuario en el historial
    historial_usuario = {
        "telefono": numero,
        "emisor": numero,
        "mensaje": mensaje_usuario,
        "hora": datetime.now().isoformat(),
        "tipo": "usuario"
    }
    guardar_en_historial(historial_usuario)

    # Buscar conocimiento en la base de datos
    respuesta_conocimiento = buscar_conocimiento(nombre_nora, mensaje_usuario)
    if respuesta_conocimiento:
        # Guardar respuesta del bot en el historial
        historial_nuevo = {
            "telefono": numero,
            "emisor": nora_numero,  # Usar número de Nora desde la configuración
            "mensaje": respuesta_conocimiento,
            "hora": datetime.now().isoformat(),
            "tipo": "respuesta"
        }
        guardar_en_historial(historial_nuevo)

        # Enviar respuesta al usuario
        enviar_mensaje(numero, respuesta_conocimiento, nombre_usuario)
        return respuesta_conocimiento

    # Si no se encuentra conocimiento, usar IA
    respuesta_ia = manejar_respuesta_ai(mensaje_usuario)

    # Guardar respuesta generada por la IA en el historial
    historial_nuevo = {
        "telefono": numero,
        "emisor": nora_numero,  # Usar número de Nora desde la configuración
        "mensaje": respuesta_ia,
        "hora": datetime.now().isoformat(),
        "tipo": "respuesta"
    }
    guardar_en_historial(historial_nuevo)

    # Enviar respuesta al usuario
    enviar_mensaje(numero, respuesta_ia, nombre_usuario)
    return respuesta_ia
