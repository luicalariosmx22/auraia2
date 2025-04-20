# Archivo: debug_supabase.py
# Este archivo contiene la función 'debug_supabase' que verifica la configuración de Supabase.

import os
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def debug_supabase():
    """
    Verifica la configuración de Supabase y la conexión con la base de datos.
    """
    try:
        # Obtener las credenciales de Supabase desde las variables de entorno
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            return {"ok": False, "error": "Faltan las credenciales de Supabase en las variables de entorno."}

        # Crear cliente de Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Verificar conexión básica: intentar listar las tablas
        response = supabase.table("bot_data").select("*").limit(1).execute()
        if response.error:
            return {"ok": False, "error": f"Error al conectar con Supabase: {response.error.message}"}

        return {"ok": True, "mensaje": "Conexión con Supabase verificada correctamente."}

    except Exception as e:
        return {"ok": False, "error": f"Excepción al verificar Supabase: {str(e)}"}