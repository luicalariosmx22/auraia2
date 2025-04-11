from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json
import os
import openai
from utils.config import cargar_configuracion
from utils.historial import guardar_en_historial
from utils.normalizador import normalizar_numero
from datetime import datetime

whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')

def obtener_base_conocimiento():
    try:
        with open('servicios_conocimiento.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook():
    mensaje_usuario = request.form.get('Body', '').strip().lower()
    numero_usuario = normalizar_numero(request.form.get('From'))
    nombre_usuario = request.form.get('ProfileName', '')

    respuesta = MessagingResponse()
    print(f"📩 Mensaje recibido: {mensaje_usuario} de {numero_usuario} ({nombre_usuario})")

    # Cargar estado de IA desde contactos_info.json
    try:
        with open('contactos_info.json', 'r', encoding='utf-8') as f:
            contactos_info = json.load(f)
        ia_activada = contactos_info.get(numero_usuario, {}).get("ia_activada", True)
    except (FileNotFoundError, json.JSONDecodeError):
        ia_activada = True
        contactos_info = {}

    # Si no existe el contacto, crearlo
    if numero_usuario not in contactos_info:
        contactos_info[numero_usuario] = {
            "nombre": nombre_usuario,
            "ia_activada": ia_activada,
            "etiquetas": [],
            "primer_mensaje": datetime.now().isoformat(),
            "ultimo_mensaje": datetime.now().isoformat(),
            "cantidad_mensajes": 1
        }
    else:
        contactos_info[numero_usuario]["ultimo_mensaje"] = datetime.now().isoformat()
        contactos_info[numero_usuario]["cantidad_mensajes"] += 1

    # Guardar cambios en contactos_info.json
    with open('contactos_info.json', 'w', encoding='utf-8') as f:
        json.dump(contactos_info, f, ensure_ascii=False, indent=2)

    # Si IA está desactivada
    if not ia_activada:
        respuesta.message("La IA está desactivada. ¿En qué puedo ayudarte de manera manual?")
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido", nombre=nombre_usuario, ia_activada=ia_activada)
        guardar_en_historial(numero_usuario, "La IA está desactivada. ¿En qué puedo ayudarte de manera manual?", tipo="enviado", nombre="Aura AI", ia_activada=ia_activada)
        return str(respuesta)

    # Respuestas automatizadas
    if mensaje_usuario in ['hola', 'buenas', 'hi', 'hello']:
        texto_bienvenida = "👋 ¡Hola! Soy *Aura AI*..."
        respuesta.message(texto_bienvenida)
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido", nombre=nombre_usuario, ia_activada=ia_activada)
        guardar_en_historial(numero_usuario, texto_bienvenida, tipo="enviado", nombre="Aura AI", ia_activada=ia_activada)
    else:
        respuesta.message("🤖 Lo siento, no tengo información sobre eso todavía.")
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido", nombre=nombre_usuario, ia_activada=ia_activada)
        guardar_en_historial(numero_usuario, "🤖 Lo siento, no tengo información sobre eso todavía.", tipo="enviado", nombre="Aura AI", ia_activada=ia_activada)

    return str(respuesta)

@whatsapp_bp.route('/enviar', methods=['POST'])
def enviar_mensaje():
    data = request.get_json()
    numero = normalizar_numero(data.get('numero'))
    mensaje = data.get('mensaje')

    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=mensaje,
            from_=from_whatsapp_number,
            to=numero
        )

        guardar_en_historial(numero, mensaje, tipo="enviado", nombre="Aura AI")
        return jsonify({"status": "ok", "sid": message.sid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500