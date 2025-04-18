from supabase import create_client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Las credenciales de Supabase no están configuradas. Verifica SUPABASE_URL y SUPABASE_KEY en tu archivo .env.")

# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)