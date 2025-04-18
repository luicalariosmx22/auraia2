from utils.supabase_client import supabase
from datetime import datetime

def guardar_mensaje(telefono, mensaje, emisor):
    """
    Guarda un mensaje en la tabla 'historial_conversaciones'.
    """
    registro = {
        "telefono": telefono,
        "mensaje": mensaje,
        "emisor": emisor,
        "timestamp": datetime.utcnow().isoformat()  # Fecha y hora en formato UTC
    }
    try:
        print(f"🔍 Intentando guardar mensaje en historial_conversaciones...")
        print(f"Datos del mensaje: {registro}")
        response = supabase.table("historial_conversaciones").insert(registro).execute()
        if response.data:
            print(f"✅ Mensaje guardado correctamente: {response.data}")
            return response
        else:
            print(f"⚠️ No se pudo guardar el mensaje en historial_conversaciones.")
            return None
    except Exception as e:
        print(f"❌ Error al guardar mensaje en historial_conversaciones: {str(e)}")
        return None
