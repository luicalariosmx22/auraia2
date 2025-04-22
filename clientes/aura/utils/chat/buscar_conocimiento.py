from clientes.aura.utils.supabase import supabase

def obtener_base_conocimiento(numero_nora):
    """
    Recupera la base de conocimiento en bloques desde la tabla 'conocimiento_nora'.
    """
    try:
        # Consulta a la tabla 'conocimiento_nora' para obtener los bloques de conocimiento
        response = supabase.table("conocimiento_nora") \
            .select("contenido") \
            .eq("numero_nora", numero_nora) \
            .order("creado_en", desc=False) \
            .execute()

        # Procesar los datos obtenidos
        data = response.data or []
        print(f"📚 {len(data)} bloques encontrados para {numero_nora}")
        return [{"contenido": row["contenido"]} for row in data]

    except Exception as e:
        # Manejo de errores
        print(f"❌ [BaseConocimiento] Error al obtener contenido por bloques: {e}")
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
