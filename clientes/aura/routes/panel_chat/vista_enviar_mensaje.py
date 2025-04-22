# clientes/aura/routes/panel_chat/vista_enviar_mensaje.py
print("✅ vista_enviar_mensaje.py cargado correctamente")

from flask import Blueprint, request, jsonify
from datetime import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.chat.leer_historial import leer_historial
from clientes.aura.utils.chat.guardar_historial import guardar_historial

# Si usas SocketIO para mensajes en tiempo real
try:
    from app import socketio  # asegúrate que esto esté disponible
except ImportError:
    socketio = None

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
