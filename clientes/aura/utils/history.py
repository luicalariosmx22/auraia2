from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_en_historial(numero, mensaje, origen, nombre):
    """
    Guarda un mensaje en la tabla `historial_conversaciones` en Supabase.
    :param numero: Número del remitente o destinatario.
    :param mensaje: Contenido del mensaje.
    :param origen: Origen del mensaje ('usuario' o 'bot').
    :param nombre: Nombre del remitente o destinatario.
    """
    nuevo_mensaje = {
        "telefono": numero,
        "mensaje": mensaje,
        "origen": origen,
        "nombre": nombre,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        response = supabase.table("historial_conversaciones").insert(nuevo_mensaje).execute()
        if not response.data:
            print(f"❌ Error al guardar en historial_conversaciones: {not response.data}")
        else:
            print(f"✅ Mensaje guardado en historial_conversaciones: {nuevo_mensaje}")
    except Exception as e:
        print(f"❌ Error al guardar en historial_conversaciones: {str(e)}")
