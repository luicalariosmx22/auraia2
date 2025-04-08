from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import traceback
from utils.normalizador import normalizar_numero
from utils.historial import guardar_en_historial
from utils.error_logger import registrar_error

api_mensajes = Blueprint('api_mensajes', __name__)

UPLOAD_FOLDER = "archivos_enviados"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_mensajes.route("/api/enviar_mensaje", methods=["POST"])
def enviar_mensaje_api():
    try:
        numero = normalizar_numero(request.form.get("numero", ""))
        mensaje = request.form.get("respuesta", "").strip()
        archivo = request.files.get("archivo")

        if not numero or not mensaje:
            return jsonify({"success": False, "error": "Número y mensaje son requeridos"}), 400

        guardar_en_historial(numero, mensaje, tipo="enviado")

        if archivo:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_guardada = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_guardada)
            # Aquí deberías agregar lógica para enviar el archivo por WhatsApp usando tu sistema actual
            print(f"📎 Archivo recibido para {numero}: {nombre_archivo}")
            # enviar_archivo_por_whatsapp(numero, ruta_guardada)  # TODO

        # También podrías integrar aquí el envío real usando Twilio u otro servicio
        print(f"✅ Mensaje para {numero}: {mensaje}")
        return jsonify({"success": True})

    except Exception as e:
        traceback.print_exc()
        registrar_error("api_mensajes", "Error al enviar mensaje por API", tipo="API", detalles=str(e))
        return jsonify({"success": False, "error": str(e)}), 500
