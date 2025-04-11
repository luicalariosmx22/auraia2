import re

def normalizar_numero(numero):
    if numero:
        numero = numero.replace("whatsapp:", "")
        numero = re.sub(r"\D", "", numero)
        if numero.startswith("521") and len(numero) == 13:
            numero = "52" + numero[3:]
        return numero
    return ""

def limpiar_mensaje(mensaje):
    if mensaje:
        return mensaje.strip().lower()
    return ""
