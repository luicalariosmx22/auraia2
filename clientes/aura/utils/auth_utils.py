# clientes/aura/utils/auth_utils.py

def is_admin_user(email):
    """
    Verifica si un correo pertenece a un administrador.
    Puedes agregar o quitar correos aquí.
    """
    admin_emails = [
        "bluetiemx@gmail.com",
        "soynoraai@gmail.com"
    ]
    return email in admin_emails

def is_module_active(nombre_nora: str, modulo: str) -> bool:
    """
    Verifica si un módulo está activo para un nombre_nora específico.
    """
    from supabase import create_client
    import os
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    res = supabase.from_("modulos_disponibles").select("activo").eq("nombre_nora", nombre_nora).eq("modulo", modulo).single().execute()
    return res.data and res.data.get("activo") is True
