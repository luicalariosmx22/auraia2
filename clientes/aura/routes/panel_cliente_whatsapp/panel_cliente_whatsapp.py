# ✅ Archivo: clientes/aura/routes/panel_cliente_whatsapp/panel_cliente_whatsapp.py
# 👉 Blueprint UI para conectar número y mostrar QR
from flask import Blueprint, render_template, request, session
from flask_socketio import emit, join_room
from supabase import create_client
from clientes.aura.utils.auth_utils import is_module_active

panel_cliente_whatsapp_bp = Blueprint("panel_cliente_whatsapp_bp", __name__, template_folder="../../templates")

@panel_cliente_whatsapp_bp.route("/panel_cliente/<nombre_nora>/whatsapp")
def whatsapp_dashboard(nombre_nora):
    if not is_module_active(nombre_nora, "whatsapp"):
        return "Módulo no activo", 403
    return render_template("panel_cliente_whatsapp.html", nombre_nora=nombre_nora)

def register_socket_handlers(socketio):
    @socketio.on("join_whatsapp")
    def _join(data):
        join_room(f"whatsapp_{data['nombre_nora']}")

    @socketio.on("whatsapp_qr")
    def _qr(data):
        emit("whatsapp_qr", data, room=f"whatsapp_{data['nombre_nora']}")
