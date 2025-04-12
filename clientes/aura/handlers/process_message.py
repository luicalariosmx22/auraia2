# 📁 Archivo: clientes/aura/handlers/process_message.py

import os
import json
from clientes.aura.utils.normalize import normalizar_numero, limpiar_mensaje
from clientes.aura.utils.history import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.utils.settings_loader import cargar_settings
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.handlers.handle_files import manejar_archivos_adjuntos
from clientes.aura.utils.comunicacion_contextual import debe_saludar, debe_preguntar_si_hay_duda

def procesar_mensaje(data):
    numero = normalizar_numero(data.get("From"))
    mensaje = limpiar_mensaje(data.get("Body"))
    nombre = data.get("ProfileName", "Usuario")

    guardar_en_historial(numero, mensaje, "usuario", nombre)

    # 🔌 Revisar si la IA está activada en config.json
    config_path = "clientes/aura/config.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        if not config.get("ia_activada", True):
            mensaje_manual = "🔕 Nora AI está en modo manual. El cliente tomará el control del chat."
            print("🛑 IA desactivada. No se procesará el mensaje automáticamente.")
            enviar_mensaje(numero, mensaje_manual, nombre)
            guardar_en_historial(numero, mensaje_manual, "bot", "Aura AI")
            return mensaje_manual

    settings = cargar_settings()
    respuesta = None

    # 1. Intentar respuestas automáticas
    if settings.get("usar_respuestas_automaticas"):
        respuesta = manejar_respuesta_keywords(mensaje)

    # 2. Intentar manejo por archivo
    if not respuesta and settings.get("usar_manejo_archivos"):
        respuesta = manejar_archivos_adjuntos(mensaje)

    # 3. Intentar respuesta con IA
    if not respuesta and settings.get("usar_ai"):
        respuesta = manejar_respuesta_ai(mensaje)

    # 4. Si IA también falla, usar último recurso (opcional)
    if not respuesta:
        respuesta = "Estoy pensando... ¿puedes darme un poco más de contexto? 🧠"

    # 5. Añadir saludo si aplica
    if debe_saludar(numero):
        respuesta = "¡Hola! Soy Nora AI 🤖 " + respuesta

    # 6. Agregar seguimiento si pasó mucho tiempo sin respuesta
    if debe_preguntar_si_hay_duda(numero):
        respuesta += "\n\n¿Quedaste con alguna duda que te pueda ayudar a resolver?"

    # 7. Enviar mensaje y registrar
    print("🧠 Respuesta generada:", respuesta)
    enviar_mensaje(numero, respuesta, nombre)
    guardar_en_historial(numero, respuesta, "bot", "Aura AI")

    return respuesta
