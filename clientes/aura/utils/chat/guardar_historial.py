# clientes/aura/utils/chat/guardar_historial.py
from datetime import datetime
from clientes.aura.utils.supabase import supabase
from app import socketio  # Importar la instancia de SocketIO

def guardar_historial(nombre_nora, telefono, mensajes):
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": telefono,
            "mensaje": m.get("texto") or m.get("mensaje"),
            "emisor": m["emisor"],
            "hora": m.get("hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "timestamp": datetime.now().isoformat()
        }
        for m in mensajes
    ]
    try:
        # Guardar los registros en la base de datos
        supabase.table("historial_conversaciones").insert(registros).execute()

        # Emitir un evento de WebSocket para cada mensaje
        for m in mensajes:
            socketio.emit('nuevo_mensaje', {
                "telefono": telefono,
                "mensaje": m.get("texto") or m.get("mensaje"),
                "emisor": m["emisor"],
                "hora": m.get("hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

