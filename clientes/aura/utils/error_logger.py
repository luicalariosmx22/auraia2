from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_error(origen, mensaje_error, tipo="General", detalles=None):
    """
    Registra un error en la tabla `logs_errores` en Supabase.

    Args:
        origen (str): Módulo o función donde ocurrió el error.
        mensaje_error (str): Descripción del error.
        tipo (str): Tipo de error (opcional, por defecto "General").
        detalles (str, optional): Información adicional sobre el error.

    Returns:
        dict: Resultado de la operación con éxito o error.
    """
    error = {
        "origen": origen,
        "mensaje": mensaje_error,
        "tipo": tipo,
        "detalles": detalles,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # Intentar registrar el error en Supabase
        response = supabase.table("logs_errores").insert(error).execute()
        if not response.data:
            print("❌ No se pudo registrar el error en Supabase.")
            return {"success": False, "error": "No se pudo registrar el error en Supabase."}
        else:
            print(f"✅ Error registrado en Supabase: {error}")
            return {"success": True, "data": response.data}
    except Exception as e:
        # Manejar errores de conexión o de Supabase
        print(f"❌ Error al conectar con Supabase: {str(e)}")
        return {"success": False, "error": str(e)}
