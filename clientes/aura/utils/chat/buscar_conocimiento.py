from clientes.aura.utils.supabase import supabase

def obtener_base_conocimiento(numero_nora):
    """
    Recupera la base de conocimiento desde la tabla 'configuracion_bot' usando el número de Nora.
    """
    try:
        respuesta = supabase.table("configuracion_bot") \
            .select("base_conocimiento") \
            .eq("numero_nora", numero_nora) \
            .single() \
            .execute(postgrest_options={"method": "POST"})  # ✅ Solución 414

        datos = respuesta.data
        if datos and datos.get("base_conocimiento"):
            print(f"✅ [BaseConocimiento] Cargado para {numero_nora}.")
            bloques = [b.strip() for b in datos["base_conocimiento"].split("\n\n") if b.strip()]
            return [{"contenido": b} for b in bloques]
        else:
            print(f"⚠️ [BaseConocimiento] No se encontró contenido para Nora: {numero_nora}")
            return []
    except Exception as e:
        print(f"❌ [BaseConocimiento] Error al obtener contenido: {e}")
        return []

def buscar_conocimiento(numero_nora, mensaje_usuario):
    """
    Construye el prompt completo usando personalidad, instrucciones y base de conocimiento.
    """
    try:
        print(f"📚 Cargando configuración para Nora con número: {numero_nora}")
        response = supabase.table("configuracion_bot") \
            .select("base_conocimiento, personalidad, instrucciones") \
            .eq("numero_nora", numero_nora) \
            .single() \
            .execute(postgrest_options={"method": "POST"})  # ✅ Solución 414

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
