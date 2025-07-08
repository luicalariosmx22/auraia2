from utils.db.bot_data import obtener_respuestas

def manejar_respuesta_keywords(mensaje_usuario):
    respuestas = obtener_respuestas()

    for r in respuestas:
        palabra = r.get("palabra_clave", "").lower()
        if palabra and palabra in mensaje_usuario.lower():
            return r.get("respuesta")

    return None
