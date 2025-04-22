# clientes/aura/utils/chat/generar_resumen.py
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_resumen_ia(mensajes):
    if not mensajes:
        return "No hay suficientes mensajes para generar un resumen."

    texto = "\n".join([f"{m['emisor']}: {m['mensaje']}" for m in mensajes[-20:]])
    prompt = f"""
Eres un asistente profesional. Resume brevemente esta conversación entre un cliente y Nora. Identifica intereses y posibles seguimientos:

{texto}

Resumen:
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error al generar resumen con IA: {e}")
        return "No se pudo generar el resumen."


# Archivos de rutas por separado ya estructurados. Listo para continuar con el resto del sistema de chat en tiempo real.
