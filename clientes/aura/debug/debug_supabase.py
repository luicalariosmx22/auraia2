# Archivo: debug_supabase.py
# Este archivo contiene funciones para verificar la configuración y conexión de Supabase.

from clientes.aura.utils.supabase_client import supabase

def run_verificacion():
    """
    Verifica la conexión con Supabase y devuelve un mensaje de estado.

    Returns:
        str: Mensaje indicando el estado de la conexión.
    """
    try:
        # Realiza una consulta simple para verificar la conexión
        response = supabase.table("contactos").select("*").limit(1).execute()
        
        # Verifica si la consulta fue exitosa
        if response.status_code != 200:
            return f"❌ Error al verificar Supabase: Código de estado {response.status_code}"
        
        # Si la consulta tiene datos, la conexión es exitosa
        if response.data:
            return "✅ Conexión con Supabase verificada correctamente."
        else:
            return "⚠️ Conexión exitosa, pero la tabla 'contactos' está vacía."
    except Exception as e:
        return f"❌ Error al conectar con Supabase: {str(e)}"