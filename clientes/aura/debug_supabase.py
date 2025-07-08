from clientes.aura.utils.supabase_client import supabase

# Add your debugging code here
def debug_supabase():
    # Example debug code
    data = supabase.table("example_table").select("*").execute()
    print(data)