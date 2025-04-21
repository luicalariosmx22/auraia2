import os
import openai
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error
from utils.supabase_client import supabase

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def cargar_base_conocimiento(nombre_nora):
    """
    Carga la base de conocimiento específica para una Nora desde Supabase.
    """
    try:
        res = supabase.table("base_conocimiento").select("contenido").eq("nombre_nora", nombre_nora).execute()
        if res.data:
            # Concatenar múltiples registros de la base de conocimiento
            return "\n".join([item["contenido"] for item in res.data])
        return ""
    except Exception as e:
        registrar_error("IA", f"No se pudo cargar el conocimiento desde Supabase para {nombre_nora}: {e}")
        return ""

def manejar_respuesta_ai(mensaje_usuario, nombre_nora="Nora", temperatura=0.7, modelo="gpt-3.5-turbo"):
    """
    Genera una respuesta utilizando OpenAI GPT-3.5-turbo basada en el mensaje del usuario y la base de conocimiento.
    """
    try:
        # Cargar la base de conocimiento específica para la Nora
        conocimiento_base = cargar_base_conocimiento(nombre_nora)

        # Construir el prompt dinámico
        prompt = f"""
Eres {nombre_nora}, una asistente profesional y personalizada.

Tu trabajo es responder de forma clara, útil, profesional y humana.
No inventes información y utiliza el conocimiento disponible siempre que sea posible.

Conocimiento disponible:
{conocimiento_base}

Pregunta del usuario:
{mensaje_usuario}

Respuesta:
        """

        # Llamar a la API de OpenAI
        respuesta = openai.ChatCompletion.create(
            model=modelo,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperatura
        )

        return respuesta.choices[0].message.content.strip()

    except openai.error.OpenAIError as e:
        registrar_error("IA", f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. Por favor, intenta nuevamente."
    except Exception as e:
        registrar_error("IA", f"Error inesperado al generar respuesta: {e}")
        return "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente."
