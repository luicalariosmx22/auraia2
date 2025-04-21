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
    Consulta el contenido largo de la memoria desde Supabase usando el número de la Nora como identificador.

    Args:
        numero_nora (str): Número de la instancia de Nora.
        mensaje_usuario (str): Mensaje enviado por el usuario.

    Returns:
        str: Prompt completo para enviar a la IA, o None si no se encuentra contenido.
    """
    try:
        print(f"📚 Buscando base de conocimiento para número_nora: {numero_nora}")
        print(f"📝 Mensaje recibido del usuario: '{mensaje_usuario}'")

        response = (
            supabase.table("base_conocimiento")
            .select("contenido")
            .eq("numero_nora", numero_nora)
            .single()
            .execute()
        )

        if not response.data:
            print(f"⚠️ [Conocimiento] No se encontró contenido para número_nora: {numero_nora}")
            return None

        contenido = response.data.get("contenido", "").strip()
        if not contenido:
            print("⚠️ [Conocimiento] El contenido está vacío.")
            return None

        print(f"✅ [Conocimiento] Conocimiento encontrado. Longitud: {len(contenido)} caracteres.")

        prompt = f"""
Eres Nora, una asistente profesional de marketing digital.

Tu trabajo es ayudar a los clientes de forma clara, útil y natural.
No inventes información. Utiliza el siguiente conocimiento siempre que sea posible.

Conocimiento disponible:
{contenido}

Pregunta del usuario:
{mensaje_usuario}

Respuesta:
"""
        print("🧠 Prompt generado y listo para enviar a la IA:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)

        return prompt

    except Exception as e:
        print(f"❌ [Conocimiento] Error al consultar conocimiento en Supabase: {e}")
        return None
