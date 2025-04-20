import uuid
from supabase import create_client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def validar_uuid(valor):
    """
    Verifica si un valor dado es un UUID válido.
    
    Args:
        valor (str): El valor a verificar.
    
    Returns:
        bool: True si el valor es un UUID válido, False en caso contrario.
    """
    try:
        uuid_obj = uuid.UUID(valor, version=4)
        return str(uuid_obj) == valor
    except ValueError:
        return False


def insertar_datos_con_uuid(tabla, datos):
    """
    Inserta datos en una tabla de Supabase con validación previa de UUID.
    
    Args:
        tabla (str): Nombre de la tabla en Supabase.
        datos (dict): Diccionario con los datos a insertar.
    
    Returns:
        dict: Respuesta de Supabase con el estado de la operación.
    """
    try:
        # Validar si todos los valores UUID en los datos son válidos
        for campo, valor in datos.items():
            if "uuid" in campo.lower() and not validar_uuid(valor):
                # Generar un UUID automáticamente si el valor es inválido
                nuevo_uuid = str(uuid.uuid4())
                print(f"⚠️ Valor inválido para {campo}: '{valor}'. Generando UUID: {nuevo_uuid}")
                datos[campo] = nuevo_uuid

        # Insertar datos en Supabase
        respuesta = supabase.table(tabla).insert(datos).execute()

        if respuesta.error:
            print(f"❌ Error al insertar en la tabla '{tabla}': {respuesta.error.message}")
        else:
            print(f"✅ Datos insertados exitosamente en '{tabla}': {respuesta.data}")

        return respuesta

    except Exception as e:
        print(f"❌ Excepción al insertar datos: {str(e)}")
        return {"error": str(e)}