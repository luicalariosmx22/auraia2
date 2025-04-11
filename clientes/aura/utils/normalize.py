# 📁 Archivo: clientes/aura/utils/normalize.py

def normalizar_numero(numero):
    """
    Asegura el formato correcto para Twilio WhatsApp:
    - Mantiene el prefijo 'whatsapp:'
    - Agrega el '1' en números móviles de México (después de +52)
    """
    if numero.startswith("whatsapp:"):
        numero = numero.replace("whatsapp:", "")

    # Corregir formato mexicano: +52 debe ir seguido de 1
    if numero.startswith("+52") and not numero.startswith("+521"):
        numero = "+521" + numero[3:]

    return f"whatsapp:{numero}"


def limpiar_mensaje(mensaje):
    """
    Limpia y normaliza el mensaje entrante:
    - Quita espacios
    - Convierte a minúsculas
    """
    return mensaje.strip().lower() if mensaje else ""
