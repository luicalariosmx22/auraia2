from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def activar_modulo_tareas_si_no_existe(nombre_nora):
    res = supabase.table("modulos_disponibles").select("id").eq("nombre_nora", nombre_nora).eq("modulo", "tareas").execute()
    if not res.data:
        supabase.table("modulos_disponibles").insert({
            "nombre_nora": nombre_nora,
            "modulo": "tareas",
            "activo": True
        }).execute()