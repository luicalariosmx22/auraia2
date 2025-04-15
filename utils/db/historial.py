from utils.supabase_client import supabase
from datetime import datetime

def guardar_mensaje(telefono, mensaje, emisor):
    registro = {
        "telefono": telefono,
        "mensaje": mensaje,
        "emisor": emisor,
        "timestamp": datetime.utcnow().isoformat()
    }
    return supabase.table("historial_conversaciones").insert(registro).execute()
