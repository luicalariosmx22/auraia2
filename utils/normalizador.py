# utils/normalizador.py

import re

def normalizar_numero(numero):
    """
    Normaliza un número a formato E.164 sin el 1 extra (solo +52XXXXXXXXXX).
    """
    if not numero:
        return ""

    # Extraer solo dígitos
    solo_digitos = re.sub(r'\D', '', numero)

    # Si ya viene con +52 y tiene 12 dígitos (ej. 521234567890), quitar el "1"
    if solo_digitos.startswith("521") and len(solo_digitos) == 13:
        return "52" + solo_digitos[3:]

    # Si empieza con 52 y tiene 12 dígitos, ya está bien
    if solo_digitos.startswith("52") and len(solo_digitos) == 12:
        return solo_digitos

    # Si es número nacional de México (10 dígitos), agregar 52
    if len(solo_digitos) == 10:
        return "52" + solo_digitos

    return solo_digitos
