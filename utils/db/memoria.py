from utils.supabase_client import supabase

def obtener_memoria(telefono):
    """
    Obtiene la memoria asociada a un número de teléfono desde la tabla 'memoria'.
    """
    try:
        print(f"🔍 Buscando memoria para el teléfono: {telefono}")
        res = supabase.table("memoria").select("*").eq("telefono", telefono).execute()
        if res.data:
            memoria = {r["clave"]: r["valor"] for r in res.data}
            print(f"✅ Memoria encontrada para {telefono}: {memoria}")
            return memoria
        else:
            print(f"⚠️ No se encontró memoria para el teléfono: {telefono}")
            return {}
    except Exception as e:
        print(f"❌ Error al obtener memoria para {telefono}: {str(e)}")
        return {}

def guardar_memoria(telefono, clave, valor):
    """
    Guarda un valor en la tabla 'memoria' asociado a un número de teléfono y una clave.
    """
    registro = {
        "telefono": telefono,
        "clave": clave,
        "valor": valor
    }
    try:
        print(f"🔍 Intentando guardar memoria: {registro}")
        response = supabase.table("memoria").insert(registro).execute()
        if response.data:
            print(f"✅ Memoria guardada correctamente: {response.data}")
            return response
        else:
            print(f"⚠️ No se pudo guardar la memoria.")
            return None
    except Exception as e:
        print(f"❌ Error al guardar memoria: {str(e)}")
        return None
