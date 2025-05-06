from clientes.aura.utils import supabase_client as supabase

def buscar_conocimiento(pregunta):
    """
    Busca conocimiento relacionado con la pregunta en la base de datos de Supabase.

    Args:
        pregunta (str): La pregunta para buscar conocimiento relacionado.

    Returns:
        list: Una lista de resultados relacionados con la pregunta.
    """
    try:
        respuesta = supabase.table("conocimiento").select("*").ilike("pregunta", f"%{pregunta}%").execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al buscar conocimiento: {e}")
        return []