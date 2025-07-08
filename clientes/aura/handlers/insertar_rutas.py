from supabase import create_client
from dotenv import load_dotenv
import os
from clientes.aura.utils.validar_uuid import validar_o_generar_uuid

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insertar_ruta(ruta, blueprint, metodo, registrado_en=None, uuid=""):
    """
    Inserta una ruta en la tabla 'rutas_registradas' en Supabase. Valida el UUID antes de la inserción.

    Args:
        ruta (str): Ruta registrada (por ejemplo, '/debug').
        blueprint (str): Nombre del blueprint asociado.
        metodo (str): Método HTTP (por ejemplo, 'GET').
        registrado_en (str): Fecha y hora de registro (opcional).
        uuid (str): UUID de la ruta (opcional).

    Returns:
        dict: Respuesta de Supabase.
    """
    uuid_valido = validar_o_generar_uuid(uuid)
    datos = {
        "id": uuid_valido,
        "ruta": ruta,
        "blueprint": blueprint,
        "metodo": metodo,
        "registrado_en": registrado_en or "NOW()"  # Usa la fecha y hora actual si no se especifica.
    }

    try:
        respuesta = supabase.table("rutas_registradas").insert(datos).execute()
        if respuesta.error:
            print(f"❌ Error al insertar en Supabase: {respuesta.error.message}")
        else:
            print(f"✅ Ruta insertada correctamente: {respuesta.data}")
        return respuesta
    except Exception as e:
        print(f"❌ Excepción al insertar ruta: {str(e)}")
        return {"error": str(e)}