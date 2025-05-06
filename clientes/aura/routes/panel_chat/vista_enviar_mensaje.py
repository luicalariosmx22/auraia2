# clientes/aura/routes/panel_chat/vista_enviar_mensaje.py
print("✅ vista_enviar_mensaje.py cargado correctamente (supabase actualizado)")

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.chat.leer_historial import leer_historial
from clientes.aura.utils.chat.guardar_historial import guardar_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.extensiones import socketio  # Importar socketio desde extensiones

vista_enviar_mensaje_bp = Blueprint("vista_enviar_mensaje", __name__)

@vista_enviar_mensaje_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    data = request.json
    telefono = normalizar_numero(data.get("numero"))
    texto = data.get("mensaje")

    if not all([telefono, texto]):
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    historial = leer_historial(telefono)
    historial.append({
        "emisor": "usuario",
        "mensaje": texto,
        "fecha": datetime.now().strftime("%d-%b %H:%M")
    })

    guardar_historial("Nora", telefono, historial)

    # Emitir en tiempo real si SocketIO está activo
    if socketio:
        socketio.emit("nuevo_mensaje", {
            "telefono": telefono,
            "mensaje": texto,
            "emisor": "usuario"
        }, broadcast=True)

    return jsonify({"success": True})

@vista_enviar_mensaje_bp.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje_chat():
    data = request.json
    numero = data.get("numero")
    mensaje = data.get("mensaje")
    nombre = data.get("nombre", "Usuario")

    if not numero or not mensaje:
        return jsonify({"error": "Faltan parámetros"}), 400

    enviar_mensaje(numero, mensaje, nombre)
    guardar_historial({
        "telefono": numero,
        "mensaje": mensaje,
        "tipo": "manual",
        "nombre_nora": data.get("nombre_nora", "nora")
    })

    # Emitir en tiempo real usando current_app para evitar ciclos circulares
    socketio = current_app.extensions.get('socketio')
    if socketio:
        socketio.emit("nuevo_mensaje", {
            "telefono": numero,
            "mensaje": mensaje,
            "emisor": "manual"
        }, broadcast=True)

    return jsonify({"success": True, "message": "Mensaje enviado y guardado correctamente."})
