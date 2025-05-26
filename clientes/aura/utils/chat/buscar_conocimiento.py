from clientes.aura.utils.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

def obtener_base_conocimiento(nombre_nora: str):
    """
    Recupera TODOS los bloques de conocimiento desde la tabla 'conocimiento_nora'
    filtrando únicamente por nombre_nora.
    """
    try:
        consulta = supabase.table("conocimiento_nora").select("contenido").eq("nombre_nora", nombre_nora)
        respuesta = consulta.execute()
        datos = respuesta.data

        if datos:
            logger.info(f"✅ [ConocimientoNora] Se cargaron {len(datos)} bloques para {nombre_nora}.")
            bloques = [
                {"titulo": "Sin título", "contenido": item["contenido"].strip()}
                for item in datos if item.get("contenido")
            ]
            return bloques

        logger.warning(f"⚠️ [ConocimientoNora] No hay bloques para {nombre_nora}.")
        return [{
            "titulo": "respuesta_default",
            "contenido": "Hola, soy Nora. ¿En qué puedo ayudarte hoy? Puedo darte información sobre cursos, automatización o estrategias digitales."
        }]

    except Exception as e:
        logger.error(f"❌ [ConocimientoNora] Error al obtener contenido: {e}")
        return [{
            "titulo": "error_fallback",
            "contenido": "Ocurrió un error al consultar la información. Pero aquí estoy para ayudarte. ¿Qué te gustaría saber?"
        }]


def buscar_conocimiento(numero_nora: str, mensaje_usuario: str):
    """
    Recupera la configuración general de la Nora y genera un prompt con personalidad e instrucciones
    usando el campo base_conocimiento de configuracion_bot (texto plano).
    """
    try:
        logger.info(f"📚 Usando contenido plano como contexto para Nora {numero_nora}")
        response = supabase.table("configuracion_bot") \
            .select("base_conocimiento, personalidad, instrucciones") \
            .eq("numero_nora", numero_nora) \
            .single() \
            .execute()

        if not response.data:
            logger.warning(f"⚠️ No se encontró configuración para {numero_nora}")
            return None

        config = response.data
        personalidad = config.get("personalidad", "profesional y amigable")
        instrucciones = config.get("instrucciones", "Responde de forma clara y útil.")
        base_conocimiento = config.get("base_conocimiento", "").strip()

        if not base_conocimiento:
            logger.warning("⚠️ La base_conocimiento está vacía.")
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

        logger.info("✅ Prompt final generado.")
        return prompt

    except Exception as e:
        logger.error(f"❌ Error generando el prompt: {e}")
        return None
