from utils.supabase_client import supabase

def obtener_contacto(telefono):
    """
    Obtiene un contacto de la tabla 'contactos' basado en el número de teléfono.
    """
    try:
        print(f"🔍 Buscando contacto con el teléfono: {telefono}")
        res = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if res.data:
            print(f"✅ Contacto encontrado: {res.data[0]}")
            return res.data[0]
        else:
            print(f"⚠️ No se encontró contacto con el teléfono: {telefono}")
            return None
    except Exception as e:
        print(f"❌ Error al obtener contacto: {str(e)}")
        return None

def insertar_contacto(contacto):
    """
    Inserta un nuevo contacto en la tabla 'contactos'.
    """
    try:
        print(f"🔍 Intentando insertar contacto: {contacto}")
        response = supabase.table("contactos").insert(contacto).execute()
        if response.data:
            print(f"✅ Contacto insertado correctamente: {response.data}")
            return response
        else:
            print(f"⚠️ No se pudo insertar el contacto.")
            return None
    except Exception as e:
        print(f"❌ Error al insertar contacto: {str(e)}")
        return None

def actualizar_contacto(telefono, data):
    """
    Actualiza un contacto existente en la tabla 'contactos' basado en el número de teléfono.
    """
    try:
        print(f"🔍 Intentando actualizar contacto con el teléfono: {telefono}")
        print(f"Datos a actualizar: {data}")
        response = supabase.table("contactos").update(data).eq("telefono", telefono).execute()
        if response.data:
            print(f"✅ Contacto actualizado correctamente: {response.data}")
            return response
        else:
            print(f"⚠️ No se pudo actualizar el contacto con el teléfono: {telefono}")
            return None
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")
        return None

def obtener_etiquetas(telefono):
    """
    Obtiene las etiquetas asociadas a un contacto basado en el número de teléfono.
    """
    try:
        print(f"🔍 Buscando etiquetas para el teléfono: {telefono}")
        res = supabase.table("etiquetas").select("*").eq("telefono", telefono).execute()
        if res.data:
            etiquetas = [e["etiqueta"] for e in res.data]
            print(f"✅ Etiquetas encontradas: {etiquetas}")
            return etiquetas
        else:
            print(f"⚠️ No se encontraron etiquetas para el teléfono: {telefono}")
            return []
    except Exception as e:
        print(f"❌ Error al obtener etiquetas: {str(e)}")
        return []

def insertar_etiqueta(telefono, etiqueta):
    """
    Inserta una nueva etiqueta asociada a un número de teléfono en la tabla 'etiquetas'.
    """
    registro = {
        "telefono": telefono,
        "etiqueta": etiqueta
    }
    try:
        print(f"🔍 Intentando insertar etiqueta: {registro}")
        response = supabase.table("etiquetas").insert(registro).execute()
        if response.data:
            print(f"✅ Etiqueta insertada correctamente: {response.data}")
            return response
        else:
            print(f"⚠️ No se pudo insertar la etiqueta: {registro}")
            return None
    except Exception as e:
        print(f"❌ Error al insertar etiqueta: {str(e)}")
        return None
