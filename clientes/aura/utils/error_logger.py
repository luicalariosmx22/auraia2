from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_error(origen, mensaje_error, tipo="general", detalles=None):
    """
    Registra un error en la tabla `logs_errores` en Supabase.
    :param origen: Módulo o función donde ocurrió el error.
    :param mensaje_error: Descripción del error.
    :param tipo: Tipo de error (opcional).
    :param detalles: Información adicional (opcional).
    """
    error = {
        "origen": origen,
        "mensaje": mensaje_error,
        "tipo": tipo,
        "detalles": detalles,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        response = supabase.table("logs_errores").insert(error).execute()
        if not response.data:
            print(f"❌ Error al registrar en Supabase: {not response.data}")
        else:
            print(f"✅ Error registrado en Supabase: {error}")
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {str(e)}")
