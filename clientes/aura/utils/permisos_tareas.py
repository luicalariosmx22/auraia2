# ✅ Archivo: clientes/aura/utils/permisos_tareas.py
# 👉 Funciones para validar permisos especiales de usuarios en el módulo de TAREAS

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ✅ Función: puede_ver_todas_tareas(usuario_id)
def puede_ver_todas_tareas(usuario_id, nombre_nora):
    res = supabase.table("usuarios_clientes").select("*").eq("id", usuario_id).eq("nombre_nora", nombre_nora).limit(1).execute()
    usuario = res.data[0] if res.data else None
    if not usuario:
        return False
    return usuario.get("ver_todas_tareas", False)

# ✅ Función: puede_reasignar_tareas(usuario_id)
def puede_reasignar_tareas(usuario_id, nombre_nora):
    res = supabase.table("usuarios_clientes").select("*").eq("id", usuario_id).eq("nombre_nora", nombre_nora).limit(1).execute()
    usuario = res.data[0] if res.data else None
    if not usuario:
        return False
    return usuario.get("reasignar_tareas", False)

# ✅ Función: puede_crear_para_otros(usuario_id)
def puede_crear_para_otros(usuario_id, nombre_nora):
    res = supabase.table("usuarios_clientes").select("*").eq("id", usuario_id).eq("nombre_nora", nombre_nora).limit(1).execute()
    usuario = res.data[0] if res.data else None
    if not usuario:
        return False
    return usuario.get("crear_tareas_otros", False)

# ✅ Función: es_supervisor(usuario_id)
def es_supervisor(usuario_id, nombre_nora):
    res = supabase.table("usuarios_clientes").select("*").eq("id", usuario_id).eq("nombre_nora", nombre_nora).limit(1).execute()
    usuario = res.data[0] if res.data else None
    if not usuario:
        return False
    return usuario.get("es_supervisor_tareas", False)

# ✅ Función: supervisores_actuales(nombre_nora)
def supervisores_actuales(nombre_nora):
    actuales = supabase.table("usuarios_clientes").select("id") \
        .eq("nombre_nora", nombre_nora).eq("es_supervisor_tareas", True).execute()
    return actuales.data

# ✅ Función: validar_limite_supervisores(cliente_id, nuevo=True)
def validar_limite_supervisores(cliente_id, nuevo=True):
    config = supabase.table("configuracion_bot").select("max_supervisores_tareas") \
        .eq("cliente_id", cliente_id).limit(1).execute()  # 🔁 CAMBIO AQUÍ
    config_data = config.data[0] if config.data else {}
    limite = config_data.get("max_supervisores_tareas", 3)

    actuales = supabase.table("usuarios_clientes").select("id") \
        .eq("empresa_id", cliente_id).eq("es_supervisor_tareas", True).execute()
    total = len(actuales.data)

    if nuevo and total >= limite:
        raise Exception(f"❌ No puedes tener más de {limite} supervisores activos.")
    return True

# ✅ Función: obtener_rol_tareas(usuario_id)
def obtener_rol_tareas(usuario_id, nombre_nora):
    res = supabase.table("usuarios_clientes").select("rol, es_supervisor_tareas").eq("id", usuario_id).eq("nombre_nora", nombre_nora).limit(1).execute()
    usuario = res.data[0] if res.data else None
    if not usuario:
        return None
    if usuario.get("rol"):
        return usuario["rol"]
    if usuario.get("es_supervisor_tareas"):
        return "supervisor"
    return "usuario"
