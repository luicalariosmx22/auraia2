# 📁 Archivo: clientes/aura/utils/normalize.py

def normalizar_numero(numero):
    """
    Asegura que el número venga con el prefijo 'whatsapp:' necesario para Twilio.
    Si ya lo tiene, lo deja igual.
    """
    if numero.startswith("whatsapp:"):
        return numero
    return f"whatsapp:{numero}"


def limpiar_mensaje(mensaje):
    """
    Limpia el mensaje recibido: lo convierte a minúsculas, elimina espacios extra y símbolos comunes.
    """
    if not mensaje:
        return ""
    return mensaje.strip().lower()
