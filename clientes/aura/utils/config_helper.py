# utils/config_helper.py

from supabase import create_client
from dotenv import load_dotenv
import os
import json

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cargar_configuracion(nombre_nora):
    """
    Cargar configuración desde Supabase.
    """
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"❌ Error al cargar configuración: {response.error}")
            return {"usar_openai": False}  # Valor predeterminado
        return response.data[0]  # Devuelve la configuración encontrada
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return {"usar_openai": False}  # Valor predeterminado

def guardar_configuracion(nombre_nora, data):
    """
    Guardar configuración en Supabase.
    """
    try:
        # Agregar el nombre de la Nora a los datos
        data["nombre_nora"] = nombre_nora
        response = supabase.table("configuracion_bot").upsert(data).execute()
        if response.error:
            print(f"❌ Error al guardar configuración: {response.error}")
        else:
            print("✅ Configuración guardada correctamente en Supabase")
    except Exception as e:
        print(f"❌ Error al guardar configuración: {str(e)}")
