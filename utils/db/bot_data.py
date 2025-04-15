from utils.supabase_client import supabase

def obtener_respuestas():
    res = supabase.table("bot_data").select("*").execute()
    return res.data if res.data else []

def buscar_por_palabra(palabra):
    res = supabase.table("bot_data").select("*").ilike("palabra_clave", f"%{palabra}%").execute()
    return res.data if res.data else []
