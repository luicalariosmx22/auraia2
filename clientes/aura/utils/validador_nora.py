# 📁 clientes/aura/utils/validador_nora.py

from clientes.aura.utils.supabase_client import supabase

def obtener_noras_validas():
    """
    Obtiene todos los nombres de Noras registrados en Supabase.
    Siempre incluye 'nora' como robot base.
    """
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora").execute()
        nombres = [item["nombre_nora"].lower() for item in response.data or []]
        return ["nora"] + nombres  # 'nora' siempre debe estar disponible
    except Exception as e:
        print(f"⚠️ Error al obtener Noras válidas desde Supabase: {e}")
        return ["nora"]

def validar_nombre_nora(nombre_recibido: str) -> str:
    """
    Valida el nombre de la Nora recibido desde un mensaje.
    - Convierte a minúsculas
    - Usa 'nora' si no se recibe nada
    - Verifica si existe en Supabase
    """
    nombre = (nombre_recibido or "").strip().lower()

    if not nombre:
        print("⚠️ No se recibió NombreNora. Usando 'nora' por defecto.")
        return "nora"

    noras_validas = obtener_noras_validas()

    if nombre not in noras_validas:
        print(f"🚨 CUIDADO: '{nombre}' no existe en configuracion_bot. Puede fallar si no es la Nora base.")

    print(f"🎯 NombreNora validado: '{nombre}'")
    return nombre
