from flask import session

def obtener_permisos():
    rol = session.get("rol", "")
    permisos = {
        "es_superadmin": rol == "superadmin",
        "es_supervisor": rol == "supervisor",
        "es_cliente": rol == "cliente"
    }
    return permisos
