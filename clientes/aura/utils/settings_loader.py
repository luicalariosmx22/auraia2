import json
import os
from supabase import create_client
from dotenv import load_dotenv

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RUTA_CONFIG = "clientes/aura/config/settings.json"

def cargar_settings():
    """
    Carga las configuraciones desde la tabla `settings` en Supabase.
    Si no se encuentran configuraciones, devuelve valores predeterminados.
    """
    try:
        response = supabase.table("settings").select("*").limit(1).execute()
        if response.error or not response.data:
            print(f"⚠️ Configuración no encontrada en Supabase. Usando valores predeterminados.")
            return {
                "usar_ai": False,
                "usar_respuestas_automaticas": False,
                "usar_manejo_archivos": False
            }
        return response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuraciones desde Supabase: {e}")
        return {
            "usar_ai": False,
            "usar_respuestas_automaticas": False,
            "usar_manejo_archivos": False
        }
