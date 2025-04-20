import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_rutas_en_supabase(app):
    try:
        print("📦 Registrando rutas activas en Supabase...")

        # (Opcional) Eliminar registros anteriores
        supabase.table("rutas_registradas").delete().neq("id", "").execute()

        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            ruta = str(rule)
            blueprint = endpoint.split(".")[0] if "." in endpoint else "root"
            metodos = list(rule.methods - {"HEAD", "OPTIONS"})

            for metodo in metodos:
                resultado = supabase.table("rutas_registradas").insert({
                    "ruta": ruta,
                    "blueprint": blueprint,
                    "metodo": metodo,
                    "registrado_en": datetime.now().isoformat()
                }).execute()
                print(f"📝 {metodo} {ruta} -> {blueprint}")

        print("✅ Rutas registradas correctamente en Supabase.")
    except Exception as e:
        print(f"❌ Error al registrar rutas en Supabase: {str(e)}")
