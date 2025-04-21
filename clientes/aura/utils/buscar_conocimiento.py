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


def buscar_conocimiento(numero_nora, mensaje_usuario):
    """
    Consulta el contenido largo de la memoria desde Supabase,
    usando el número de la Nora como identificador principal.

    Args:
        numero_nora (str): Número de la instancia de Nora.
        mensaje_usuario (str): Mensaje enviado por el usuario.

    Returns:
        str: Prompt completo para enviar a la IA, o None si no se encuentra contenido.
    """
    try:
        print(f"📚 Buscando conocimiento para número_nora: {numero_nora} y mensaje: '{mensaje_usuario}'")

        # Realizar la consulta en la tabla base_conocimiento
        response = (
            supabase.table("base_conocimiento")
            .select("contenido")
            .eq("numero_nora", numero_nora)  # Filtrar por número de Nora
            .single()
            .execute()
        )

        # Verificar si hay datos en la respuesta
        if not response.data:
            print(f"⚠️ No se encontró contenido para número_nora: {numero_nora}")
            return None

        contenido = response.data.get("contenido", "")
        if not contenido.strip():
            print("⚠️ Contenido vacío para esta Nora.")
            return None

        # 🧠 Formar el prompt completo para enviar a la IA
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
        print("✅ Prompt generado exitosamente.")
        return prompt

    except Exception as e:
        print(f"❌ Error al consultar conocimiento en Supabase: {e}")
        return None
