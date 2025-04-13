import json
import os
from datetime import datetime

ARCHIVO_HISTORIAL = "historial_conversaciones.json"
ARCHIVO_CONTACTOS = "contactos_info.json"

def guardar_en_historial(remitente, mensaje, tipo="recibido", nombre=None, ia_activada=True, etiquetas=[]):
    # Cargar historial
    try:
        with open(ARCHIVO_HISTORIAL, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historial = []

    # Añadir mensaje
    historial.append({
        "remitente": remitente,
        "mensaje": mensaje,
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "ia_activada": ia_activada,
        **({"nombre": nombre} if nombre else {})
    })

    # Guardar historial
    with open(ARCHIVO_HISTORIAL, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

    # Actualizar contactos_info
    try:
        with open(ARCHIVO_CONTACTOS, 'r', encoding='utf-8') as f:
            contactos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        contactos = {}

    if remitente not in contactos:
        contactos[remitente] = {
            "nombre": nombre,
            "ia_activada": ia_activada,
            "etiquetas": etiquetas,
            "mensaje_count": 1,
            "primer_mensaje": datetime.now().isoformat(),
            "ultimo_mensaje": datetime.now().isoformat()
        }
    else:
        contactos[remitente].update({
            "ultimo_mensaje": datetime.now().isoformat(),
            "mensaje_count": contactos[remitente].get("mensaje_count", 0) + 1,
            "ia_activada": ia_activada
        })

    with open(ARCHIVO_CONTACTOS, 'w', encoding='utf-8') as f:
        json.dump(contactos, f, ensure_ascii=False, indent=2)