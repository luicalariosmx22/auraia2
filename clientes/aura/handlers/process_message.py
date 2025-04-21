# 📁 clientes/aura/handlers/process_message.py

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

def procesar_mensaje(data):
    # Obtener datos del mensaje
    numero = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")
    nombre_nora = data.get("NombreNora", "Nora")  # ✅ Dinámico: Obtener el nombre de Nora desde los datos

    guardar_en_historial(numero, mensaje_usuario, "usuario", nombre_nora)

    # Buscar conocimiento en la base de datos
    respuesta_conocimiento = buscar_conocimiento(nombre_nora, mensaje_usuario)
    if respuesta_conocimiento:
        guardar_en_historial(numero, respuesta_conocimiento, "bot", nombre_nora)
        enviar_mensaje(numero, respuesta_conocimiento, nombre_usuario)
        return respuesta_conocimiento

    # Si no se encuentra conocimiento, usar IA
    respuesta_ia = manejar_respuesta_ai(mensaje_usuario)
    guardar_en_historial(numero, respuesta_ia, "bot", nombre_nora)
    enviar_mensaje(numero, respuesta_ia, nombre_usuario)
    return respuesta_ia
