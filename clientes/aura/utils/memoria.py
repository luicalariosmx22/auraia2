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
    try:
        response = supabase.table("memoria_usuarios").select("*").eq("usuario_id", usuario_id).execute()
        if response.error or not response.data:
            print(f"⚠️ Memoria no encontrada para el usuario {usuario_id}.")
            return {}
        return response.data[0].get("data", {})
    except Exception as e:
        print(f"❌ Error al obtener memoria para el usuario {usuario_id}: {str(e)}")
        return {}

def guardar_memoria(usuario_id, data):
    """
    Guarda un nuevo estado de memoria para el usuario en Supabase.
    """
    try:
        # Verificar si ya existe una memoria para el usuario
        response = supabase.table("memoria_usuarios").select("*").eq("usuario_id", usuario_id).execute()
        if response.error:
            print(f"❌ Error al verificar memoria existente: {response.error}")
            return

        if response.data:
            # Actualizar memoria existente
            response = supabase.table("memoria_usuarios").update({"data": data}).eq("usuario_id", usuario_id).execute()
            if response.error:
                print(f"❌ Error al actualizar memoria para el usuario {usuario_id}: {response.error}")
            else:
                print(f"✅ Memoria actualizada para el usuario {usuario_id}.")
        else:
            # Crear nueva memoria
            nueva_memoria = {"usuario_id": usuario_id, "data": data}
            response = supabase.table("memoria_usuarios").insert(nueva_memoria).execute()
            if response.error:
                print(f"❌ Error al guardar nueva memoria para el usuario {usuario_id}: {response.error}")
            else:
                print(f"✅ Nueva memoria guardada para el usuario {usuario_id}.")
    except Exception as e:
        print(f"❌ Error al guardar memoria para el usuario {usuario_id}: {str(e)}")

def limpiar_memoria(usuario_id):
    """
    Elimina la memoria del usuario en Supabase si ya no se necesita.
    """
    try:
        response = supabase.table("memoria_usuarios").delete().eq("usuario_id", usuario_id).execute()
        if response.error:
            print(f"❌ Error al eliminar memoria para el usuario {usuario_id}: {response.error}")
        else:
            print(f"✅ Memoria eliminada para el usuario {usuario_id}.")
    except Exception as e:
        print(f"❌ Error al eliminar memoria para el usuario {usuario_id}: {str(e)}")
