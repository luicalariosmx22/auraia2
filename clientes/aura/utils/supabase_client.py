import os
from supabase import create_client

# 🚀 Leemos variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Creamos el cliente y lo exportamos como `supabase`
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ supabase_client.py cargado correctamente y cliente listo")