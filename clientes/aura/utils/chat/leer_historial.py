# clientes/aura/utils/chat/leer_historial.py
from supabase import create_client
from dotenv import load_dotenv
import os
from clientes.aura.utils.normalizador import normalizar_numero

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leer_historial(telefono, limite=20, offset=0):
    telefono = normalizar_numero(telefono)
    numero_simplificado = telefono[-10:]
    try:
        response = (
            supabase
            .table("historial_conversaciones")
            .select("*")
            .like("telefono", f"%{numero_simplificado}")
            .order("hora", desc=False)
            .range(offset, offset + limite - 1)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"❌ Error al leer historial: {str(e)}")
        return []
