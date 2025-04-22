# utils/normalizador.py

import re

def normalizar_numero(numero):
    """
    Normaliza un número de WhatsApp eliminando caracteres no numéricos
    y asegurando que tenga formato internacional E.164 (ej: 521XXXXXXXXXX).

    Casos manejados:
    - Números en formato E.164 (521XXXXXXXXXX o 1XXXXXXXXXX) se devuelven sin cambios.
    - Números con prefijo incompleto (52XXXXXXXXXX) se corrigen agregando el '1'.
    - Números nacionales de México (10 dígitos) se convierten a formato E.164.
    - Si el número no es válido, se devuelve una cadena vacía.

    Ejemplos:
    - Entrada: "whatsapp:5216629360887" -> Salida: "5216629360887"
    - Entrada: "52XXXXXXXXXX" -> Salida: "521XXXXXXXXXX"
    - Entrada: "XXXXXXXXXX" -> Salida: "521XXXXXXXXXX"
    """
    if not numero:
        return ""

    # Extraer solo dígitos
    solo_digitos = re.sub(r'\D', '', numero)

    # Si ya viene con formato completo E.164 válido
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

    # Si no cumple con ningún caso, devolver vacío
    return ""

print(normalizar_numero("whatsapp:5216629360887"))  # Salida: 5216629360887
print(normalizar_numero("52XXXXXXXXXX"))           # Salida: 521XXXXXXXXXX
print(normalizar_numero("XXXXXXXXXX"))             # Salida: 521XXXXXXXXXX
print(normalizar_numero("1XXXXXXXXXX"))            # Salida: 1XXXXXXXXXX
print(normalizar_numero(""))                       # Salida: ""
print(normalizar_numero(None))                     # Salida: ""
