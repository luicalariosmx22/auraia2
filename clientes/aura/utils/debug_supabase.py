from clientes.aura.utils.supabase_client import supabase

# Add your debugging functions here
def debug_function():
    # Example debug function
    print("Debugging Supabase")
    supabase.table("nombre_tabla").select(...).execute()