# utils/normalizador.py

import re

def normalizar_numero(numero):
    """
    Normaliza un número de WhatsApp eliminando caracteres no numéricos,
    asegurando que tenga formato internacional E.164 (ej: 521XXXXXXXXXX).
    """
    if not numero:
        return ""

    # Extraer solo dígitos
    solo_digitos = re.sub(r'\D', '', numero)

    # Si ya viene con formato completo E.164 válido (ej. 521XXXXXXXXXX o 1XXXXXXXXXX)
    if solo_digitos.startswith("521") and len(solo_digitos) == 13:
        return solo_digitos
    if solo_digitos.startswith("1") and len(solo_digitos) == 11:
        return solo_digitos

    # Si viene como 52XXXXXXXXXX (falta el 1 para WhatsApp), completarlo
    if solo_digitos.startswith("52") and len(solo_digitos) == 12:
        return "521" + solo_digitos[2:]

    # Si es número nacional de México (10 dígitos)
    if len(solo_digitos) == 10:
        return "521" + solo_digitos

    return solo_digitos
