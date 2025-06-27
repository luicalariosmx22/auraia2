from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("email"):
            return redirect("/login/simple")
        return f(*args, **kwargs)
    return decorated_function

def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("email") or not session.get("nombre_nora"):
            return redirect("/login/simple")
        return f(*args, **kwargs)
    return decorated_function

def login_required_cliente_debug(f):
    """Versión debug del decorador para investigar problemas de sesión"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🔍 DEBUG - Verificando sesión para: {f.__name__}")
        print(f"📊 Session keys: {list(session.keys())}")
        print(f"📧 Email: {session.get('email', 'NO ENCONTRADO')}")
        print(f"🎯 Nombre Nora: {session.get('nombre_nora', 'NO ENCONTRADO')}")
        print(f"👤 User: {session.get('user', 'NO ENCONTRADO')}")
        print(f"🔑 Is Admin: {session.get('is_admin', 'NO ENCONTRADO')}")
        
        email_ok = bool(session.get("email"))
        nora_ok = bool(session.get("nombre_nora"))
        
        print(f"✅ Email OK: {email_ok}")
        print(f"✅ Nora OK: {nora_ok}")
        
        if not email_ok or not nora_ok:
            print(f"❌ Sesión inválida, redirigiendo a login")
            return redirect("/login/simple")
        
        print(f"✅ Sesión válida, continuando...")
        return f(*args, **kwargs)
    return decorated_function
