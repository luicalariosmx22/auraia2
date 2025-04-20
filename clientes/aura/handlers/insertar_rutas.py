from supabase import create_client
from dotenv import load_dotenv
import os
from clientes.aura.utils.validar_uuid import validar_o_generar_uuid

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insertar_ruta(nombre, uuid=""):
    """
    Inserta una ruta en la tabla 'rutas' en Supabase. Valida el UUID antes de la inserción.

    Args:
        nombre (str): Nombre de la ruta.
        uuid (str): UUID de la ruta (opcional).

    Returns:
        dict: Respuesta de Supabase.
    """
    uuid_valido = validar_o_generar_uuid(uuid)
    datos = {
        "id": uuid_valido,
        "nombre": nombre
    }

    try:
        respuesta = supabase.table("rutas").insert(datos).execute()
        if respuesta.error:
            print(f"❌ Error al insertar en Supabase: {respuesta.error.message}")
        else:
            print(f"✅ Ruta insertada correctamente: {respuesta.data}")
        return respuesta
    except Exception as e:
        print(f"❌ Excepción al insertar ruta: {str(e)}")
        return {"error": str(e)}