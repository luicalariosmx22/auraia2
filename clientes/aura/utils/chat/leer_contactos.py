from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leer_contactos(nombre_nora):
    print(f"📥 Leyendo contactos para nombre_nora: {nombre_nora}")
    try:
        response = (
            supabase
            .table("contactos")
            .select("*")
            .eq("nombre_nora", nombre_nora)
            .order("ultimo_mensaje", desc=True)
            .execute()
        )
        print(f"✅ Contactos obtenidos de Supabase: {response.data}")
        return response.data or []
    except Exception as e:
        print(f"❌ Error al leer contactos para {nombre_nora}: {str(e)}")
        return []
