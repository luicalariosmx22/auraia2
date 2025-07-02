from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from .auth_supabase import login_required_supabase, login_required_ajax_supabase

def login_required(f):
    """Decorador legacy - redirige al nuevo sistema"""
    return login_required_supabase(f)

def login_required_cliente(f):
    """Decorador legacy - redirige al nuevo sistema Supabase"""
    return login_required_supabase(f)

def login_required_ajax(f):
    """Decorador legacy para AJAX - redirige al nuevo sistema Supabase"""
    return login_required_ajax_supabase(f)

def login_required_ajax_debug(f):
    """Decorador legacy para AJAX con debug - redirige al nuevo sistema Supabase"""
    return login_required_ajax_supabase(f)

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

def login_required_ajax(f):
    """Decorador para endpoints AJAX que devuelve JSON en lugar de redirect"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Detectar si es una request AJAX
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Content-Type') == 'application/json' or
            'application/json' in request.headers.get('Accept', '')
        )
        
        if not session.get("email") or not session.get("nombre_nora"):
            if is_ajax:
                return jsonify({
                    "success": False, 
                    "message": "Sesión expirada. Por favor, inicia sesión nuevamente.",
                    "error": "authentication_required"
                }), 401
            else:
                return redirect("/login/simple")
        
        return f(*args, **kwargs)
    return decorated_function

def login_required_ajax_debug(f):
    """Versión debug del decorador AJAX para investigar problemas de sesión"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🔍 AJAX DEBUG - Verificando sesión para: {f.__name__}")
        print(f"📊 Session keys: {list(session.keys())}")
        print(f"📧 Email: {session.get('email', 'NO ENCONTRADO')}")
        print(f"🎯 Nombre Nora: {session.get('nombre_nora', 'NO ENCONTRADO')}")
        
        # Detectar si es una request AJAX
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Content-Type') == 'application/json' or
            'application/json' in request.headers.get('Accept', '')
        )
        print(f"📡 Es AJAX: {is_ajax}")
        
        email_ok = bool(session.get("email"))
        nora_ok = bool(session.get("nombre_nora"))
        
        print(f"✅ Email OK: {email_ok}")
        print(f"✅ Nora OK: {nora_ok}")
        
        if not email_ok or not nora_ok:
            print(f"❌ Sesión inválida")
            if is_ajax:
                print(f"📡 Devolviendo error JSON para AJAX")
                return jsonify({
                    "success": False, 
                    "message": "Sesión expirada. Por favor, inicia sesión nuevamente.",
                    "error": "authentication_required",
                    "debug": {
                        "email_ok": email_ok,
                        "nora_ok": nora_ok,
                        "session_keys": list(session.keys())
                    }
                }), 401
            else:
                print(f"🔄 Redirigiendo a login para request normal")
                return redirect("/login/simple")
        
        print(f"✅ Sesión válida, continuando...")
        return f(*args, **kwargs)
    return decorated_function
