from supabase import create_client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Las variables SUPABASE_URL o SUPABASE_KEY no están configuradas correctamente en el entorno. Verifica tu archivo .env.")

# 🚀 Cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Debug para confirmar que está cargado correctamente
print("✅ [Supabase] Cliente cargado correctamente y listo para usar.")