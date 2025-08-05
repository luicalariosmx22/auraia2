import os
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_supabase_client():
    """Obtiene el cliente de Supabase utilizando variables de entorno."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("No se encontraron las credenciales de Supabase en las variables de entorno")
    
    return create_client(url, key)