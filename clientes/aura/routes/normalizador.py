from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import traceback
from utils.normalizador import normalizar_numero
from utils.historial import guardar_en_historial
from utils.error_logger import registrar_error
from twilio.rest import Client

api_mensajes = Blueprint('api_mensajes', __name__)

UPLOAD_FOLDER = "archivos_enviados"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Función corregida para enviar mensaje de texto por Twilio (formato E.164)
def enviar_mensaje_por_twilio(numero, mensaje):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=mensaje,
            from_=f'whatsapp:{twilio_number}',
            to=f'whatsapp:{numero}'
        )
    except Exception as e:
        registrar_error("twilio", "Error enviando mensaje con Twilio", tipo="Twilio", detalles=str(e))

@api_mensajes.route("/api/enviar_mensaje", methods=["POST"])
def enviar_mensaje_api():
    try:
        numero = normalizar_numero(request.form.get("numero", ""))
        mensaje = request.form.get("respuesta", "").strip()
        archivo = request.files.get("archivo")

        if not numero:
            return jsonify({"success": False, "error": "Número es requerido"}), 400

        # Guardar y enviar mensaje si existe
        if mensaje:
            guardar_en_historial(numero, mensaje, tipo="enviado")
            enviar_mensaje_por_twilio(numero, mensaje)
            print(f"✅ Mensaje para {numero}: {mensaje}")

            current_app.extensions['socketio'].emit("nuevo_mensaje", {
                "remitente": "bot",
                "mensaje": mensaje,
                "nombre": "Nora AI"
            })

        # Guardar archivo si existe (no se envía aún por Twilio)
        if archivo:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_guardada = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_guardada)

            print(f"📎 Archivo recibido para {numero}: {nombre_archivo}")
            guardar_en_historial(numero, f"[Archivo adjunto: {nombre_archivo}]", tipo="enviado")

            current_app.extensions['socketio'].emit("nuevo_mensaje", {
                "remitente": "bot",
                "mensaje": f"[Archivo adjunto: {nombre_archivo}]",
                "nombre": "Nora AI"
            })

        if not mensaje and not archivo:
            return jsonify({"success": False, "error": "Debes enviar un mensaje o un archivo"}), 400

        return jsonify({"success": True})

    except Exception as e:
        traceback.print_exc()
        registrar_error("api_mensajes", "Error al enviar mensaje por API", tipo="API", detalles=str(e))
        return jsonify({"success": False, "error": str(e)}), 500
