# ✅ Archivo: clientes/aura/utils/supabase_client.py
# 👉 Mejora con diagnóstico visible al cargar Supabase y manejo de error

from supabase import create_client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Instancia del cliente (será inicializada por get_supabase_client)
_supabase_client = None

def get_supabase_client():
    """
    Función para obtener el cliente de Supabase.
    Reutiliza la instancia existente o crea una nueva si no existe.
    
    Returns:
        client: Cliente de Supabase inicializado
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    print("🔍 SUPABASE_URL:", repr(SUPABASE_URL))
    print("🔍 SUPABASE_KEY presente:", bool(SUPABASE_KEY and SUPABASE_KEY.strip()))
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ Las credenciales de Supabase no están configuradas. Verifica SUPABASE_URL y SUPABASE_KEY en tu archivo .env.")
    
    # Crear cliente de Supabase con manejo de error
    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente Supabase creado correctamente")
        return _supabase_client
    except Exception as e:
        print("❌ Error al crear cliente Supabase:", str(e))
        raise e
