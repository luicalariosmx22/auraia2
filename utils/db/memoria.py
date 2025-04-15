from utils.supabase_client import supabase

def obtener_memoria(telefono):
    res = supabase.table("memoria").select("*").eq("telefono", telefono).execute()
    return {r["clave"]: r["valor"] for r in res.data} if res.data else {}

def guardar_memoria(telefono, clave, valor):
    return supabase.table("memoria").insert({
        "telefono": telefono,
        "clave": clave,
        "valor": valor
    }).execute()
