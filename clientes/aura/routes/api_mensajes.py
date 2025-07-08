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
        twilio_number = os.getenv('TWILIO_PHONE_NUMBER')  # Ya incluye whatsapp:+5255...

        if not account_sid or not auth_token or not twilio_number:
            raise Exception("Faltan credenciales de Twilio en el entorno")

        client = Client(account_sid, auth_token)

        # Verificar si el número ya contiene "whatsapp:", sino agregarlo
        if not numero.startswith("whatsapp:"):
            numero = f"whatsapp:{numero}"

        client.messages.create(
            body=mensaje,
            from_=twilio_number,
            to=numero
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

        # Obtener nombre_nora dinámico si viene en el formulario, por ahora default
        nombre_nora = request.form.get("nombre_nora", "nora")
        nombre_display = "Nora AI"

        if not numero:
            return jsonify({"success": False, "error": "Número es requerido"}), 400

        if not mensaje and not archivo:
            return jsonify({"success": False, "error": "Debes enviar un mensaje o un archivo"}), 400

        # ✅ Enviar mensaje de texto
        if mensaje:
            guardar_en_historial(
                telefono=numero,
                mensaje=mensaje,
                origen=os.getenv("TWILIO_PHONE_NUMBER", "5210000000000"),
                nombre_nora=nombre_nora,  # Puedes hacerlo dinámico si es necesario
                tipo="enviado",
                nombre=nombre_display
            )
            enviar_mensaje_por_twilio(numero, mensaje)
            print(f"✅ Mensaje enviado a {numero}: {mensaje}")

            current_app.extensions['socketio'].emit("nuevo_mensaje", {
                "remitente": "bot",
                "mensaje": mensaje,
                "nombre": nombre_display
            })

        # ✅ Guardar archivo adjunto en historial y panel
        if archivo:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_guardada = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_guardada)

            texto_archivo = f"[Archivo adjunto: {nombre_archivo}]"
            guardar_en_historial(
                telefono=numero,
                mensaje=texto_archivo,
                origen=os.getenv("TWILIO_PHONE_NUMBER", "5210000000000"),
                nombre_nora=nombre_nora,  # Puedes hacerlo dinámico si es necesario
                tipo="enviado",
                nombre=nombre_display
            )

            print(f"📎 Archivo guardado para {numero}: {nombre_archivo}")
            current_app.extensions['socketio'].emit("nuevo_mensaje", {
                "remitente": "bot",
                "mensaje": texto_archivo,
                "nombre": nombre_display
            })

        return jsonify({"success": True})

    except Exception as e:
        traceback.print_exc()
        registrar_error("api_mensajes", "Error general en enviar_mensaje_api", tipo="API", detalles=str(e))
        return jsonify({"success": False, "error": str(e)}), 500
