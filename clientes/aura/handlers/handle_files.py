def manejar_archivos_adjuntos(mensaje):
    if any(palabra in mensaje for palabra in ["brochure", "presentación", "información completa"]):
        return "Aquí tienes nuestro brochure con toda la información completa: https://agenciaaura.mx/brochure.pdf"

    return None
