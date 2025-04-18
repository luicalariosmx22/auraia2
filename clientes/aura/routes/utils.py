import json 
import os
import re
from supabase import create_client
from dotenv import load_dotenv

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def cargar_datos_supabase(tabla, filtro=None, default=None):
    """
    Carga datos desde una tabla en Supabase.
    :param tabla: Nombre de la tabla en Supabase.
    :param filtro: Diccionario con filtros opcionales (ej: {"id": "123"}).
    :param default: Valor predeterminado si no se encuentran datos.
    :return: Datos de la tabla o el valor predeterminado.
    """
    try:
        query = supabase.table(tabla).select("*")
        if filtro:
            for key, value in filtro.items():
                query = query.eq(key, value)
        response = query.execute()
        if not response.data:
            print(f"❌ Error al cargar datos de {tabla}: {not response.data}")
            return default
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar datos de {tabla}: {str(e)}")
        return default

def guardar_datos_supabase(tabla, datos):
    """
    Guarda datos en una tabla de Supabase.
    :param tabla: Nombre de la tabla en Supabase.
    :param datos: Diccionario o lista de diccionarios con los datos a guardar.
    :return: True si se guardaron correctamente, False en caso de error.
    """
    try:
        response = supabase.table(tabla).insert(datos).execute()
        if not response.data:
            print(f"❌ Error al guardar datos en {tabla}: {not response.data}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error al guardar datos en {tabla}: {str(e)}")
        return False

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
