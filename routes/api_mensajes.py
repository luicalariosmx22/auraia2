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

        if not numero:
            return jsonify({"success": False, "error": "Número es requerido"}), 400

        # Guardar mensaje si existe
        if mensaje:
            guardar_en_historial(numero, mensaje, tipo="enviado")
            print(f"✅ Mensaje para {numero}: {mensaje}")

        # Guardar archivo si existe
        if archivo:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_guardada = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_guardada)

            # Lógica simulada de envío
            print(f"📎 Archivo recibido para {numero}: {nombre_archivo}")
            guardar_en_historial(numero, f"[Archivo adjunto: {nombre_archivo}]", tipo="enviado")

            # TODO: enviar_archivo_por_whatsapp(numero, ruta_guardada)

        if not mensaje and not archivo:
            return jsonify({"success": False, "error": "Debes enviar un mensaje o un archivo"}), 400

        return jsonify({"success": True})

    except Exception as e:
        traceback.print_exc()
        registrar_error("api_mensajes", "Error al enviar mensaje por API", tipo="API", detalles=str(e))
        return jsonify({"success": False, "error": str(e)}), 500
