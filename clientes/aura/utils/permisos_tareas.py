# ✅ Archivo: clientes/aura/utils/permisos_tareas.py
# 👉 Funciones para validar permisos especiales de usuarios en el módulo de TAREAS

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ✅ Función: puede_ver_todas_tareas(usuario_id)
def puede_ver_todas_tareas(usuario_id):
    result = supabase.table("usuarios_empresa").select("ver_todas_tareas") \
        .eq("id", usuario_id).single().execute()
    return result.data.get("ver_todas_tareas", False)

# ✅ Función: puede_reasignar_tareas(usuario_id)
def puede_reasignar_tareas(usuario_id):
    result = supabase.table("usuarios_empresa").select("reasignar_tareas") \
        .eq("id", usuario_id).single().execute()
    return result.data.get("reasignar_tareas", False)

# ✅ Función: puede_crear_para_otros(usuario_id)
def puede_crear_para_otros(usuario_id):
    result = supabase.table("usuarios_empresa").select("crear_tareas_otros") \
        .eq("id", usuario_id).single().execute()
    return result.data.get("crear_tareas_otros", False)

# ✅ Función: es_supervisor(usuario_id)
def es_supervisor(usuario_id):
    result = supabase.table("usuarios_empresa").select("es_supervisor_tareas") \
        .eq("id", usuario_id).single().execute()
    return result.data.get("es_supervisor_tareas", False)

# ✅ Función: validar_limite_supervisores(cliente_id, nuevo=True)
def validar_limite_supervisores(cliente_id, nuevo=True):
    config = supabase.table("configuracion_bot").select("max_supervisores_tareas") \
        .eq("cliente_id", cliente_id).single().execute()
    limite = config.data.get("max_supervisores_tareas", 3)

    actuales = supabase.table("usuarios_empresa").select("id") \
        .eq("empresa_id", cliente_id).eq("es_supervisor_tareas", True).execute()
    total = len(actuales.data)

    if nuevo and total >= limite:
        raise Exception(f"❌ No puedes tener más de {limite} supervisores activos.")
    return True
