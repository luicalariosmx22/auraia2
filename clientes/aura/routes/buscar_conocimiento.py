from clientes.aura.utils.supabase import supabase

def buscar_conocimiento(nombre_nora, mensaje_usuario):
    """
    Busca en la tabla base_conocimiento alguna respuesta relevante al mensaje del usuario.
    Prioriza coincidencias por pregunta o tema, y devuelve la respuesta más prioritaria si existe.

    Args:
        nombre_nora (str): Nombre de la instancia de Nora.
        mensaje_usuario (str): Mensaje enviado por el usuario.

    Returns:
        str: Respuesta relevante encontrada en la base de conocimiento, o None si no se encuentra.
    """
    if not mensaje_usuario.strip():
        print("⚠️ El mensaje del usuario está vacío. No se puede buscar conocimiento.")
        return None

    try:
        # Realizar la consulta en la tabla base_conocimiento
        respuesta = supabase.table("base_conocimiento") \
            .select("respuesta") \
            .eq("nombre_nora", nombre_nora) \
            .or_(f"pregunta.ilike.%{mensaje_usuario}%,tema.ilike.%{mensaje_usuario}%") \
            .order("prioridad", desc=True) \
            .limit(1) \
            .execute()

        # Procesar los datos obtenidos
        datos = respuesta.data
        if datos and len(datos) > 0:
            print(f"✅ Conocimiento encontrado: {datos[0]['respuesta']}")
            return datos[0]["respuesta"]

        print("⚠️ No se encontró conocimiento relevante.")
        return None

    except Exception as e:
        print(f"❌ Error al buscar conocimiento: {e}")
        return None
