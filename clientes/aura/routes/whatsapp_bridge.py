# ✅ Archivo: clientes/aura/routes/whatsapp_bridge.py
# 👉 Puente Socket.IO que re‑emite eventos del worker a la UI
from flask_socketio import SocketIO, emit

def init_whatsapp_bridge(socketio: SocketIO):
    @socketio.on("whatsapp_qr")
    def qr_from_worker(data):
        emit("whatsapp_qr", data, room=f"whatsapp_{data['nombre_nora']}", include_self=False)

    @socketio.on("whatsapp_ready")
    def ready_from_worker(data):
        emit("whatsapp_ready", data, room=f"whatsapp_{data['nombre_nora']}", include_self=False)

    @socketio.on("whatsapp_status")
    def status_from_worker(data):
        emit("whatsapp_status", data, room=f"whatsapp_{data['nombre_nora']}", include_self=False)

    @socketio.on("whatsapp_in")
    def incoming_msg(data):
        emit("whatsapp_in", data, room=f"whatsapp_{data['nombre_nora']}", include_self=False)

    @socketio.on("whatsapp_out_delivered")
    def out_msg(data):
        emit("whatsapp_out_delivered", data, room=f"whatsapp_{data['nombre_nora']}", include_self=False)

    @socketio.on("whatsapp_error")
    def error_msg(data):
        emit("whatsapp_error", data, room=f"whatsapp_{data['nombre_nora']}", include_self=False)
