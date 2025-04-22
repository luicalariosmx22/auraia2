from clientes.aura.utils.supabase import supabase

def obtener_base_conocimiento(numero_nora, titulo=None):
    """
    Recupera múltiples bloques de conocimiento desde la tabla 'conocimiento_nora'
    filtrando por numero_nora y opcionalmente por título.
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
        else:
            print(f"⚠️ [ConocimientoNora] No hay bloques para {numero_nora} con el título especificado.")
            return []
    except Exception as e:
        print(f"❌ [ConocimientoNora] Error al obtener contenido: {e}")
        return []

def buscar_conocimiento(numero_nora, mensaje_usuario):
    try:
        print(f"📚 Cargando configuración para Nora con número: {numero_nora}")
        response = supabase.table("configuracion_bot") \
            .select("base_conocimiento, personalidad, instrucciones") \
            .eq("numero_nora", numero_nora) \
            .single() \
            .execute()  # ✅ CORREGIDO

        if not response.data:
            print(f"⚠️ No se encontró configuración para {numero_nora}")
            return None

        config = response.data
        personalidad = config.get("personalidad", "profesional y amigable")
        instrucciones = config.get("instrucciones", "Responde de forma clara y útil.")
        base_conocimiento = config.get("base_conocimiento", "").strip()

        if not base_conocimiento:
            print("⚠️ La base_conocimiento está vacía.")
            return None

        prompt = f"""
Eres Nora, una asistente profesional.

Tu personalidad: {personalidad}
Instrucciones clave: {instrucciones}

Conocimiento disponible:
{base_conocimiento}

Pregunta del usuario:
{mensaje_usuario}

Respuesta:"""

        print("✅ Prompt final generado.")
        return prompt

    except Exception as e:
        print(f"❌ Error generando el prompt: {e}")
        return None
