from clientes.aura.utils.supabase_client import supabase

supabase.table("nombre_tabla").select(...).execute()