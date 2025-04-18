from utils.supabase_client import supabase
from datetime import datetime

def guardar_mensaje(telefono, mensaje, emisor, nombre_nora):
    """
    Guarda un mensaje en la tabla 'historial_conversaciones'.
    """
    registro = {
        "telefono": telefono,
        "mensaje": mensaje,
        "emisor": emisor,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Hora actual
        "nombre_nora": nombre_nora,  # Asegúrate de pasar este valor
        "timestamp": datetime.utcnow().isoformat()  # Timestamp en UTC
    }
    try:
        print("🔍 Intentando guardar mensaje en historial_conversaciones...")
        print(f"Datos del mensaje: {registro}")
        response = supabase.table("historial_conversaciones").insert(registro).execute()
        if response.data:
            print(f"✅ Mensaje guardado correctamente: {response.data}")
            return response
        else:
            print("⚠️ No se pudo guardar el mensaje en historial_conversaciones.")
            return None
    except Exception as e:
        print(f"❌ Error al guardar mensaje en historial_conversaciones: {str(e)}")
        return None
