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
