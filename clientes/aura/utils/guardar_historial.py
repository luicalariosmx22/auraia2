from clientes.aura.utils.supabase_client import supabase

def guardar_historial(data):
    """
    Guarda el historial en la base de datos de Supabase.

    Args:
        data (dict): Datos a guardar en el historial.
    """
    try:
        supabase.insert(data)
    except Exception as e:
        print(f"Error al guardar el historial: {e}")