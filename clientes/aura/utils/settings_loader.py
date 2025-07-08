# clientes/aura/utils/settings_loader.py

import os
from supabase import create_client
from dotenv import load_dotenv

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cargar_settings(nombre_nora="aura"):
    """
    Carga las configuraciones desde la tabla `configuracion` en Supabase.
    Si no se encuentran configuraciones, devuelve valores predeterminados.
    """
    try:
        response = supabase.table("configuracion").select("*").eq("nombre_nora", nombre_nora).limit(1).execute()
        if not response.data:
            print(f"⚠️ Configuración no encontrada para '{nombre_nora}' en Supabase. Usando valores predeterminados.")
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
