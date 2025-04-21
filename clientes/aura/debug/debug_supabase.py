# Archivo: debug_supabase.py
# Este archivo contiene funciones para verificar la configuración y conexión de Supabase.

from clientes.aura.utils.supabase import supabase

def run_verificacion():
    """
    Verifica la conexión con Supabase y devuelve un mensaje de estado.

    Returns:
        str: Mensaje indicando el estado de la conexión.
    """
    try:
        # Realiza una consulta simple para verificar la conexión
        response = supabase.table("nombre_de_tu_tabla").select("*").limit(1).execute()
        if response.error:
            return f"❌ Error al verificar Supabase: {response.error.message}"
        return "✅ Conexión con Supabase verificada correctamente."
    except Exception as e:
        return f"❌ Error al conectar con Supabase: {str(e)}"