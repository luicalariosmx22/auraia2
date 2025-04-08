from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import emit
import os
import traceback
from utils.normalizador import normalizar_numero
from utils.historial import guardar_en_historial
from utils.error_logger import registrar_error
from app import socketio

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

        mensaje_final = mensaje

        # Guardar archivo si existe
        if archivo:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_guardada = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_guardada)
            mensaje_archivo = f"[Archivo adjunto: {nombre_archivo}]"
            guardar_en_historial(numero, mensaje_archivo, tipo="enviado")
            mensaje_final += f" 📎 {nombre_archivo}" if mensaje else mensaje_archivo

            # TODO: enviar_archivo_por_whatsapp(numero, ruta_guardada)

        # Guardar mensaje si existe
        if mensaje:
            guardar_en_historial(numero, mensaje, tipo="enviado")

        if not mensaje and not archivo:
            return jsonify({"success": False, "error": "Debes enviar un mensaje o un archivo"}), 400

        # Emitir por Socket.IO para mostrar en el chat del panel
        socketio.emit("nuevo_mensaje", {
            "remitente": "bot",
            "mensaje": mensaje_final,
            "numero": numero,
            "nombre": "Tú"
        })

        return jsonify({"success": True})

    except Exception as e:
        traceback.print_exc()
        registrar_error("api_mensajes", "Error al enviar mensaje por API", tipo="API", detalles=str(e))
        return jsonify({"success": False, "error": str(e)}), 500
