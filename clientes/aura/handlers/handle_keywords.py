def manejar_respuesta_keywords(mensaje):
    if "diseño web" in mensaje:
        return "Claro, hacemos diseño y desarrollo web personalizado. ¿Qué tipo de página necesitas?"

    if "anuncios" in mensaje:
        return "Te ayudamos con anuncios en Facebook, Instagram, Google y más. ¿En qué plataforma estás interesado?"

    if "asesoría" in mensaje:
        return "Ofrecemos asesoría personalizada en marketing digital. ¿Te gustaría agendar una llamada?"

    return None
