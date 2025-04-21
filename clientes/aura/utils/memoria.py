from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_memoria(usuario_id):
    """
    Devuelve un diccionario con la memoria del usuario si existe en Supabase.
    """
    if not usuario_id:
        print("⚠️ El usuario_id está vacío. No se puede obtener la memoria.")
        return {"success": False, "error": "usuario_id vacío"}

    try:
        response = supabase.table("memoria_usuarios").select("*").eq("usuario_id", usuario_id).execute()
        if not response.data:
            print(f"⚠️ Memoria no encontrada para el usuario {usuario_id}.")
            return {"success": True, "data": {}}
        return {"success": True, "data": response.data[0].get("data", {})}
    except Exception as e:
        print(f"❌ Error al obtener memoria para el usuario {usuario_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def guardar_memoria(usuario_id, data):
    """
    Guarda o actualiza el estado de memoria para el usuario en Supabase.
    """
    if not usuario_id or not isinstance(data, dict):
        print("⚠️ El usuario_id o los datos son inválidos. No se puede guardar la memoria.")
        return {"success": False, "error": "usuario_id o datos inválidos"}

    try:
        # Intentar actualizar o insertar en una sola operación
        response = supabase.table("memoria_usuarios").upsert({
            "usuario_id": usuario_id,
            "data": data
        }).execute()

        if not response.data:
            print(f"❌ Error al guardar memoria para el usuario {usuario_id}.")
            return {"success": False, "error": "Error al guardar memoria"}
        print(f"✅ Memoria guardada para el usuario {usuario_id}.")
        return {"success": True}
    except Exception as e:
        print(f"❌ Error al guardar memoria para el usuario {usuario_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def limpiar_memoria(usuario_id):
    """
    Elimina la memoria del usuario en Supabase si ya no se necesita.
    """
    if not usuario_id:
        print("⚠️ El usuario_id está vacío. No se puede limpiar la memoria.")
        return {"success": False, "error": "usuario_id vacío"}

    try:
        response = supabase.table("memoria_usuarios").delete().eq("usuario_id", usuario_id).execute()
        if not response.data:
            print(f"❌ Error al eliminar memoria para el usuario {usuario_id}.")
            return {"success": False, "error": "Error al eliminar memoria"}
        print(f"✅ Memoria eliminada para el usuario {usuario_id}.")
        return {"success": True}
    except Exception as e:
        print(f"❌ Error al eliminar memoria para el usuario {usuario_id}: {str(e)}")
        return {"success": False, "error": str(e)}
