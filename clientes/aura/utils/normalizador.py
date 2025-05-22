# utils/normalizador.py

import re

def normalizar_numero(numero):
    """
    Normaliza un número de WhatsApp al formato internacional E.164 para WhatsApp.
    
    Casos que maneja:
    - Quita cualquier prefijo como "whatsapp:", "+" o espacios.
    - Acepta formatos con guiones, paréntesis, etc.
    - Si es un número de México (10 o 12 dígitos), le agrega el '521'.
    - Si es de EE.UU. y empieza con '1', lo deja.
    - Devuelve el número limpio como string E.164 (ej: 521XXXXXXXXXX).
    """
    if not numero:
        return ""

    # Remover prefijos innecesarios
    numero = str(numero).strip().lower().replace("whatsapp:", "").replace("+", "")

    # Extraer solo los dígitos
    solo_digitos = re.sub(r'\D', '', numero)

    # 🇲🇽 Caso 1: ya está en formato 521XXXXXXXXXX
    if solo_digitos.startswith("521") and len(solo_digitos) == 13:
        return solo_digitos

    # 🇲🇽 Caso 2: está como 52XXXXXXXXXX → falta el "1"
    if solo_digitos.startswith("52") and len(solo_digitos) == 12:
        return "521" + solo_digitos[2:]

    # 🇲🇽 Caso 3: número nacional de 10 dígitos
    if len(solo_digitos) == 10:
        return "521" + solo_digitos

    # 🇺🇸 Caso 4: número de USA tipo 1XXXXXXXXXX
    if solo_digitos.startswith("1") and len(solo_digitos) == 11:
        return solo_digitos

    # ❌ Si no cumple ningún caso
    return ""

# 👇 Solo si lo ejecutas como script
if __name__ == "__main__":
    ejemplos = [
        "whatsapp:5216629360887",
        "+5216629360887",
        "52-1662-936-0887",
        "6629360887",
        "(662) 936 0887",
        "1-323-456-7890",
        "+1 (323) 456-7890",
        None,
        ""
    ]

    for e in ejemplos:
        print(f"{e:25} ➜ {normalizar_numero(e)}")
