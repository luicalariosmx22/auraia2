from clientes.aura.utils.supabase import supabase

def obtener_base_conocimiento_segura(numero_nora: str, titulo: str = None):
    """
    Recupera los bloques de conocimiento desde Supabase de forma segura.
    Siempre devuelve al menos un bloque por defecto si no hay contenido.
    """
    try:
        # Construir la consulta base
        consulta = supabase.table("conocimiento_nora").select("contenido, titulo").eq("numero_nora", numero_nora)

        # Agregar filtro por título si se proporciona
        if titulo:
            consulta = consulta.eq("titulo", titulo)

        # Ejecutar la consulta
        respuesta = consulta.execute()
        datos = respuesta.data

        if datos:
            print(f"✅ [ConocimientoNora] Se cargaron {len(datos)} bloques para {numero_nora}.")
            bloques = [{"titulo": item.get("titulo", "Sin título"), "contenido": item["contenido"].strip()} for item in datos if item.get("contenido")]
            return bloques

        # Si no hay datos, devolver un bloque predeterminado
        print(f"⚠️ [ConocimientoNora] No hay bloques para {numero_nora} con el título especificado.")
        return [{
            "titulo": "respuesta_default",
            "contenido": "Hola, soy Nora. ¿En qué puedo ayudarte hoy? Puedo darte información sobre cursos, automatización o estrategias digitales."
        }]

    except Exception as e:
        # En caso de error, devolver un bloque de fallback
        print(f"❌ [ConocimientoNora] Error al obtener contenido: {e}")
        return [{
            "titulo": "error_fallback",
            "contenido": "Ocurrió un error al consultar la información. Pero aquí estoy para ayudarte. ¿Qué te gustaría saber?"
        }]
