# 📁 clientes/aura/handlers/process_message.py

from clientes.aura.utils.normalizador import normalizar_numero  # ✅ Actualizado
from clientes.aura.utils.limpieza import limpiar_mensaje  # ✅ Actualizado
from clientes.aura.utils.history import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.utils.settings_loader import cargar_settings
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.handlers.handle_files import manejar_archivos_adjuntos
from clientes.aura.utils.comunicacion_contextual import debe_saludar, debe_preguntar_si_hay_duda

# ✅ NUEVO: importar desde Supabase
from utils.db.contactos import obtener_contacto

def procesar_mensaje(data):
    numero = normalizar_numero(data.get("From"))
    mensaje = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")  # Renombrado para evitar confusión
    nombre_nora = "Aura AI"  # Asegúrate de obtener este valor dinámicamente si es necesario

    guardar_en_historial(numero, mensaje, "usuario", nombre_nora)

    settings = cargar_settings(nombre_nora)
    respuesta = None

    # ✅ Consultar si el contacto tiene IA desactivada
    contacto = obtener_contacto(numero)
    if contacto and contacto.get("ia_activada") is False:
        mensaje_manual = "🔕 Nora AI está en modo manual. El cliente tomará el control del chat."
        enviar_mensaje(numero, mensaje_manual, nombre_usuario)
        guardar_en_historial(numero, mensaje_manual, "bot", nombre_nora)
        return mensaje_manual

    # === 1. Respuesta automática ===
    if settings.get("usar_respuestas_automaticas"):
        respuesta = manejar_respuesta_keywords(mensaje)

    # === 2. Archivos ===
    if not respuesta and settings.get("usar_manejo_archivos"):
        respuesta = manejar_archivos_adjuntos(mensaje)

    # === 3. Inteligencia Artificial ===
    if not respuesta and settings.get("usar_ai"):
        respuesta = manejar_respuesta_ai(mensaje)

    # === 4. Último recurso
    if not respuesta:
        respuesta = "Estoy pensando... ¿puedes darme un poco más de contexto? 🧠"

    # === 5. Saludo contextual
    if debe_saludar(numero):
        respuesta = "¡Hola! Soy Nora AI 🤖 " + respuesta

    # === 6. Preguntar si tiene dudas
    if debe_preguntar_si_hay_duda(numero):
        respuesta += "\n\n¿Quedaste con alguna duda que te pueda ayudar a resolver?"

    # === 7. Enviar y guardar
    print("🧠 Respuesta generada:", respuesta)
    enviar_mensaje(numero, respuesta, nombre_usuario)
    guardar_en_historial(numero, respuesta, "bot", nombre_nora)

    return respuesta
