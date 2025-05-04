# clientes/aura/utils/chat/leer_contactos.py
import json
import os

def leer_contactos(nombre_nora):
    """
    Lee los contactos desde el archivo correspondiente a la Nora AI específica.
    """
    ruta_contactos = f"clientes/{nombre_nora}/data/contactos.json"

    if not os.path.exists(ruta_contactos):
        return []

    with open(ruta_contactos, "r", encoding="utf-8") as f:
        contactos = json.load(f)

    return contactos
