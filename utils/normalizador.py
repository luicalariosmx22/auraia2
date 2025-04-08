# routes/api_mensajes.py

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

# ✅ Enviar mensaje de texto por Twilio
def enviar_mensaje_por_twilio(numero, mensaje):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

        if not account_sid or not auth_token or not twilio_number:
            raise Exception("Faltan credenciales de Twilio en el entorno")

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=mensaje,
            from_=f'whatsapp:{twilio_number}',
            to=f'whatsapp:{numero}'
        )
    except Exception as e:
        registrar_error("twilio", "Error enviando mensaje con Twilio", tipo="Twilio", detalles=str(e))
        raise

@api_mensajes.route("/api/enviar_mensaje", methods=["POST"])
def enviar_mensaje_api():
    try:
        numero = normalizar_numero(request.form.get("numero", ""))
        mensaje = request.form.get("respuesta", "").strip()
        archivo = request.files.get("archivo")

        if not numero:
            return jsonify({"success": False, "error": "Número es requerido"}), 400

        if not mensaje and not archivo:
            return jsonify({"success": False, "error": "Debes enviar un mensaje o un archivo"}), 400

        # Enviar mensaje de texto
        if mensaje:
            guardar_en_historial(numero, mensaje, tipo="enviado")
            enviar_mensaje_por_twilio(numero, mensaje)
            print(f"✅ Mensaje enviado a {numero}: {mensaje}")

            current_app.extensions['socketio'].emit("nuevo_mensaje", {
                "remitente": "bot",
                "mensaje": mensaje,
                "nombre": "Nora AI"
            })

        # Guardar archivo adjunto (solo historial y SocketIO, no se envía por Twilio)
        if archivo:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_guardada = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_guardada)

            texto_archivo = f"[Archivo adjunto: {nombre_archivo}]"
            guardar_en_historial(numero, texto_archivo, tipo="enviado")

            print(f"📎 Archivo guardado para {numero}: {nombre_archivo}")
            current_app.extensions['socketio'].emit("nuevo_mensaje", {
                "remitente": "bot",
                "mensaje": texto_archivo,
                "nombre": "Nora AI"
            })

        return jsonify({"success": True})

    except Exception as e:
        traceback.print_exc()
        registrar_error("api_mensajes", "Error general en enviar_mensaje_api", tipo="API", detalles=str(e))
        return jsonify({"success": False, "error": str(e)}), 500
