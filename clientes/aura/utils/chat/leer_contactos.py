# clientes/aura/utils/chat/leer_contactos.py
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leer_contactos(nombre_nora):
    """
    Lee los contactos filtrando por la Nora AI específica (columna 'nora').
    """
    try:
        response = supabase.table("contactos").select("*").eq("nora", nombre_nora).execute()
        return response.data or []
    except Exception as e:
        print(f"❌ Error al leer contactos para {nombre_nora}: {str(e)}")
        return []
