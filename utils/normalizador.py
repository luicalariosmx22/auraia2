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

    # Si empieza con 521 y tiene 13 dígitos, ya está bien
    if solo_digitos.startswith("521") and len(solo_digitos) == 13:
        return solo_digitos

    # Si empieza con 52 y tiene 12 dígitos (sin el 1), añadir el 1
    if solo_digitos.startswith("52") and len(solo_digitos) == 12:
        return "521" + solo_digitos[2:]

    # Si es número nacional (10 dígitos), agregar 521 para México
    if len(solo_digitos) == 10:
        return "521" + solo_digitos

    # Si empieza con 1 y tiene 11 dígitos (USA), lo dejamos igual
    if solo_digitos.startswith("1") and len(solo_digitos) == 11:
        return solo_digitos

    return solo_digitos
