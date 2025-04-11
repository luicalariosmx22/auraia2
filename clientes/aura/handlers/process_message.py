from clientes.aura.utils.normalize import normalizar_numero, limpiar_mensaje
from clientes.aura.utils.history import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.utils.settings_loader import cargar_settings
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.handlers.handle_files import manejar_archivos_adjuntos

def procesar_mensaje(data):
    numero = normalizar_numero(data.get("From"))
    mensaje = limpiar_mensaje(data.get("Body"))
    nombre = data.get("ProfileName", "Usuario")

    guardar_en_historial(numero, mensaje, "usuario", nombre)

    settings = cargar_settings()

    respuesta = None

    if settings.get("usar_respuestas_automaticas"):
        respuesta = manejar_respuesta_keywords(mensaje)

    if not respuesta and settings.get("usar_manejo_archivos"):
        respuesta = manejar_archivos_adjuntos(mensaje)

    if not respuesta and settings.get("usar_ai"):
        respuesta = manejar_respuesta_ai(mensaje)

    if not respuesta:
        respuesta = "No entendí bien, ¿puedes repetirlo?"

    enviar_mensaje(numero, respuesta)
    guardar_en_historial(numero, respuesta, "bot", "Aura AI")

    return respuesta
