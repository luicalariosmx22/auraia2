from clientes.aura.utils.supabase import supabase

def cargar_base_conocimiento(nombre_nora):
    """
    Carga el contenido de la base de conocimiento para una instancia específica de Nora.
    Puede venir de un archivo o de Supabase.

    Args:
        nombre_nora (str): Nombre de la instancia de Nora.

    Returns:
        str: Contenido de la base de conocimiento como texto plano, o None si no se encuentra.
    """
    try:
        # Realizar la consulta en la tabla base_conocimiento
        respuesta = supabase.table("base_conocimiento") \
            .select("contenido") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        datos = respuesta.data
        if datos:
            print(f"✅ Base de conocimiento cargada para Nora: {nombre_nora}")
            return datos["contenido"]

        print(f"⚠️ No se encontró base de conocimiento para Nora: {nombre_nora}")
        return None

    except Exception as e:
        print(f"❌ Error al cargar base de conocimiento: {e}")
        return None


def buscar_conocimiento(nombre_nora, mensaje_usuario):
    """
    Busca en la base de conocimiento alguna respuesta relevante al mensaje del usuario.

    Args:
        nombre_nora (str): Nombre de la instancia de Nora.
        mensaje_usuario (str): Mensaje enviado por el usuario.

    Returns:
        str: Respuesta relevante encontrada en la base de conocimiento, o None si no se encuentra.
    """
    print(f"🔍 Buscando conocimiento para Nora: {nombre_nora}, mensaje: '{mensaje_usuario}'")

    try:
        # Realizar la consulta en la tabla base_conocimiento
        response = (
            supabase.table("base_conocimiento")
            .select("pregunta,respuesta")
            .eq("nombre_nora", nombre_nora.lower())  # Normalizar el nombre de Nora a minúsculas
            .execute()
        )

        # Verificar si hay datos en la respuesta
        if not response.data:
            print("⚠️ No se encontró conocimiento para esta Nora.")
            return None

        # Buscar coincidencias en las preguntas
        for fila in response.data:
            pregunta = fila.get("pregunta", "").lower()
            if mensaje_usuario.lower() in pregunta:
                print(f"✅ Coincidencia con pregunta: '{pregunta}' → Respuesta: {fila.get('respuesta')}")
                return fila.get("respuesta")

        print("❌ No se encontró ninguna coincidencia en preguntas.")
        return None

    except Exception as e:
        print(f"❌ Error al buscar conocimiento: {e}")
        return None
