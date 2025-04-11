def construir_mensaje_con_botones(contenido, botones):
    if not botones:
        return contenido

    mensaje = contenido.strip() + "\n\n"
    for boton in botones:
        if boton.get("tipo") == "link":
            texto = boton.get("texto", "Abrir")
            url = boton.get("url", "#")
            mensaje += f"🔗 {texto}: {url}\n"

    return mensaje.strip()
