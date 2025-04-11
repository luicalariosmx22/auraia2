import json
import os

def cargar_json(archivo, default=None):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def guardar_json(archivo, data):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
