# clientes/aura/utils/limpieza.py

def limpiar_mensaje(mensaje):
    """
    Limpia el texto del mensaje eliminando espacios en blanco al inicio y al final.
    También puedes expandir esta función más adelante si deseas eliminar emojis, símbolos, etc.
    """
    if not mensaje:
        return ""
    return mensaje.strip()
