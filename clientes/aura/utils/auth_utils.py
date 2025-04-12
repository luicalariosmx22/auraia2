# clientes/aura/utils/auth_utils.py

def is_admin_user(email):
    """Verifica si el usuario es administrador basado en su correo."""
    admin_emails = ["bluetiemx@gmail.com", "soynoraai@gmail.com"]
    return email in admin_emails
