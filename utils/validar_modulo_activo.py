# ✅ Archivo: clientes/aura/utils/validar_modulo_activo.py
# 👉 Función para verificar si un módulo está activo para una Nora desde Supabase

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def modulo_activo_para_nora(nombre_nora: str, nombre_modulo: str) -> bool:
    try:
        response = supabase.table("modulos_disponibles") \
            .select("*") \
            .eq("nora", nombre_nora) \
            .eq("modulo", nombre_modulo) \
            .execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"❌ Error verificando módulo '{nombre_modulo}' para Nora '{nombre_nora}': {e}")
        return False
