from utils.supabase_client import supabase

def obtener_contacto(telefono):
    res = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
    return res.data[0] if res.data else None

def insertar_contacto(contacto):
    try:
        print(f"Intentando insertar contacto: {contacto}")
        response = supabase.table("contactos").insert(contacto).execute()
        print(f"Respuesta de Supabase: {response}")
        return response
    except Exception as e:
        print(f"❌ Error al insertar contacto: {str(e)}")
        return None

def actualizar_contacto(telefono, data):
    return supabase.table("contactos").update(data).eq("telefono", telefono).execute()

def obtener_etiquetas(telefono):
    res = supabase.table("etiquetas_contacto").select("*").eq("telefono", telefono).execute()
    return [e["etiqueta"] for e in res.data] if res.data else []
