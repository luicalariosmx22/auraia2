# clientes/aura/utils/chat/guardar_historial.py
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.extensions.socketio_instance import socketio

def guardar_historial(data):
    registros = [
        {
            "nombre_nora": data["nombre_nora"],
            "telefono": data["telefono"],
            "mensaje": data["mensaje"],
            "tipo": data.get("tipo", "manual"),
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().isoformat()
        }
    ]
    try:
        # Guardar los registros en la base de datos
        supabase.table("historial_conversaciones").insert(registros).execute()

        # Emitir un evento de WebSocket
        socketio.emit('nuevo_mensaje', {
            "telefono": data["telefono"],
            "mensaje": data["mensaje"],
            "emisor": "usuario",
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

