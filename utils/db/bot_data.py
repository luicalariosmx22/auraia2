from utils.supabase_client import supabase

def obtener_respuestas():
    """
    Obtiene todas las respuestas de la tabla 'bot_data'.
    """
    try:
        print("🔍 Obteniendo todas las respuestas de la tabla 'bot_data'...")
        res = supabase.table("bot_data").select("*").execute()
        if res.data:
            print(f"✅ Respuestas obtenidas: {res.data}")
            return res.data
        else:
            print("⚠️ No se encontraron respuestas en la tabla 'bot_data'.")
            return []
    except Exception as e:
        print(f"❌ Error al obtener respuestas: {str(e)}")
        return []

def buscar_por_palabra(palabra):
    """
    Busca respuestas en la tabla 'bot_data' que coincidan con una palabra clave.
    """
    try:
        print(f"🔍 Buscando respuestas que coincidan con la palabra clave: {palabra}")
        res = supabase.table("bot_data").select("*").ilike("palabra_clave", f"%{palabra}%").execute()
        if res.data:
            print(f"✅ Respuestas encontradas para '{palabra}': {res.data}")
            return res.data
        else:
            print(f"⚠️ No se encontraron respuestas para la palabra clave: {palabra}")
            return []
    except Exception as e:
        print(f"❌ Error al buscar respuestas para la palabra clave '{palabra}': {str(e)}")
        return []
