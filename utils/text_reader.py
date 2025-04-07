import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def cargar_conocimiento_desde_txt(ruta_archivo="servicios_conocimiento.txt"):
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def buscar_respuesta_en_txt(pregunta, conocimiento):
    mensaje = pregunta.lower()
    bloques = conocimiento.split("\n\n")

    bloque_relevante = None
    for bloque in bloques:
        if mensaje in bloque.lower():
            bloque_relevante = bloque.strip()
            break

    if not bloque_relevante:
        for bloque in bloques:
            if any(p in bloque.lower() for p in mensaje.split()):
                bloque_relevante = bloque.strip()
                break

    if bloque_relevante:
        prompt = (
            f"Eres Aura AI, la inteligencia artificial de Aura Marketing.\n"
            f"A continuación tienes información de un servicio:\n\n"
            f"{bloque_relevante}\n\n"
            f"Con base en esa información, responde de forma clara, conversacional y amable "
            f"a este mensaje del usuario:\n\n"
            f"\"{pregunta}\"\n\n"
            f"Si es posible, resume o adapta el contenido para que se entienda fácil."
        )

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ Error al consultar OpenAI: {str(e)}"

    return None
