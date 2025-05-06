from clientes.aura.utils import supabase_client as supabase

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
        respuesta = supabase.table("base_conocimiento") \
            .select("contenido") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        datos = respuesta.data
        if datos:
            print(f"✅ [BaseConocimiento] Contenido cargado para Nora '{nombre_nora}'. Longitud: {len(datos['contenido'])} caracteres.")
            return datos["contenido"]

        print(f"⚠️ [BaseConocimiento] No se encontró contenido para Nora: {nombre_nora}")
        return None

    except Exception as e:
        print(f"❌ [BaseConocimiento] Error al cargar base de conocimiento: {e}")
        return None


def buscar_conocimiento(numero_nora, mensaje_usuario):
    """
    Construye el prompt para la IA usando la personalidad, instrucciones y base_conocimiento desde Supabase.

    Args:
        numero_nora (str): Número de la instancia de Nora.
        mensaje_usuario (str): Mensaje enviado por el usuario.

    Returns:
        str: Prompt completo para enviar a la IA, o None si no se encuentra configuración.
    """
    try:
        print(f"📚 Buscando configuración para número_nora: {numero_nora}...")
        # Traer toda la configuración de esa Nora
        response = (
            supabase.table("configuracion_bot")
            .select("*")
            .eq("numero_nora", numero_nora)
            .single()
            .execute()
        )

        if not response.data:
            print(f"⚠️ No se encontró configuración para {numero_nora}")
            return None

        config = response.data
        base_conocimiento = config.get("base_conocimiento", "").strip()
        personalidad = config.get("personalidad", "profesional y amigable")
        instrucciones = config.get("instrucciones", "Responde de forma clara y útil. No inventes.")

        if not base_conocimiento:
            print("⚠️ La base_conocimiento está vacía.")
            return None

        print(f"✅ Configuración cargada para Nora: {numero_nora}")
        print(f"🧠 Personalidad: {personalidad}")
        print(f"📋 Instrucciones: {instrucciones}")
        print(f"📚 Conocimiento base (primeros 150 caracteres): {base_conocimiento[:150]}...")

        prompt = f"""
Eres Nora, una asistente profesional.

Tu personalidad: {personalidad}
Instrucciones clave: {instrucciones}

Conocimiento disponible:
{base_conocimiento}

Pregunta del usuario:
{mensaje_usuario}

Respuesta:"""

        print("✅ Prompt generado para la IA. Listo para enviar.")
        return prompt

    except Exception as e:
        print(f"❌ Error al construir el prompt para la IA: {e}")
        return None
