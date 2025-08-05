"""
🔒 Sistema de Autenticación Mejorado para AuraAI2
- Integración completa con Supabase
- Modo dev solo en localhost
- Manejo de sesiones seguro
"""

import os
from functools import wraps
from flask import session, redirect, url_for, jsonify, request, current_app

def es_localhost():
    """Detecta si estamos ejecutando en localhost"""
    host = request.host.lower()
    return any(x in host for x in ['localhost:', '127.0.0.1:', '0.0.0.0:'])

def es_desarrollo():
    """Detecta si estamos en modo desarrollo - REQUIERE ACTIVACIÓN MANUAL"""
    if not es_localhost():
        return False
    
    # SOLO activar desarrollo si se activa explícitamente con AURA_DEV_MODE
    # NO más activación automática con FLASK_ENV
    return os.getenv('AURA_DEV_MODE') == 'True'

def login_required_supabase(f):
    """
    Decorador principal que requiere autenticación Supabase
    Solo permite bypass en localhost Y con activación manual
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # � DEBUG: Verificar estado de desarrollo
        es_dev = es_desarrollo()
        print(f"🔍 DEBUG auth_supabase:")
        print(f"   - Host: {request.host}")
        print(f"   - Es localhost: {es_localhost()}")
        print(f"   - AURA_DEV_MODE: {os.getenv('AURA_DEV_MODE')}")
        print(f"   - Es desarrollo: {es_dev}")
        print(f"   - Email en sesión: {session.get('email')}")
        
        # �🔧 BYPASS SOLO EN LOCALHOST PARA DESARROLLO (con activación manual)
        if es_dev:
            print(f"🏠 MODO DESARROLLO DETECTADO en {request.host} - Bypass de autenticación")
            if not session.get("email"):
                session["email"] = "dev@localhost.com"
                session["name"] = "Desarrollador Local"
                session["nombre_nora"] = "aura"
                session["is_admin"] = True
                session["user"] = {
                    "id": "dev-id",
                    "email": "dev@localhost.com",
                    "nombre": "Desarrollador Local",
                    "nombre_nora": "aura",
                    "rol": "admin"
                }
                session.permanent = True
                print(f"🔧 Sesión de desarrollo creada automáticamente")
        
        # Verificar sesión normal
        if not session.get("email") or not session.get("nombre_nora"):
            print(f"❌ Sesión no válida en {request.host}, redirigiendo a login")
            return redirect(url_for("simple_login_unique.login_simple"))
        
        print(f"✅ Sesión válida para {session.get('email')} en {request.host}")
        return f(*args, **kwargs)
    return decorated_function

def login_required_ajax_supabase(f):
    """
    Decorador para endpoints AJAX con autenticación Supabase
    Solo permite bypass en localhost
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Detectar si es AJAX
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Content-Type') == 'application/json' or
            'application/json' in request.headers.get('Accept', '')
        )
        
        # 🔧 BYPASS SOLO EN LOCALHOST PARA DESARROLLO
        if es_desarrollo():
            if not session.get("email"):
                session["email"] = "dev@localhost.com"
                session["name"] = "Desarrollador Local"
                session["nombre_nora"] = "aura"
                session["is_admin"] = True
                session["user"] = {
                    "id": "dev-id",
                    "email": "dev@localhost.com",
                    "nombre": "Desarrollador Local",
                    "nombre_nora": "aura",
                    "rol": "admin"
                }
                session.permanent = True
        
        # Verificar sesión
        if not session.get("email") or not session.get("nombre_nora"):
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": "Sesión expirada. Por favor, inicia sesión nuevamente.",
                    "error": "authentication_required"
                }), 401
            else:
                return redirect(url_for("simple_login_unique.login_supabase"))
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorador que requiere permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin", False):
            return jsonify({
                "success": False,
                "message": "Acceso denegado. Se requieren permisos de administrador.",
                "error": "access_denied"
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def verificar_usuario_supabase(email):
    """
    Verifica si el usuario existe en Supabase y está activo
    """
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("correo", email) \
            .eq("activo", True) \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"✅ Usuario encontrado en Supabase: {usuario['nombre']}")
            return usuario
        else:
            print(f"❌ Usuario no encontrado en Supabase: {email}")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando usuario en Supabase: {e}")
        return None

def establecer_sesion_supabase(usuario):
    """Establece la sesión con datos de Supabase"""
    session.permanent = True
    session["email"] = usuario["correo"]
    session["name"] = usuario["nombre"]
    session["nombre_nora"] = usuario.get("nombre_nora", "aura")
    session["is_admin"] = es_administrador_supabase(usuario)
    session["user"] = {
        "id": usuario["id"],
        "email": usuario["correo"],
        "nombre": usuario["nombre"],
        "nombre_nora": usuario.get("nombre_nora", "aura"),
        "rol": usuario.get("rol", "cliente"),
        "modulos": usuario.get("modulos", {}),
        "es_supervisor": usuario.get("es_supervisor", False)
    }
    session.modified = True
    
    print(f"🔐 Sesión Supabase establecida para {usuario['correo']}")
    print(f"📊 Permisos: Admin={session['is_admin']}, Rol={usuario.get('rol')}")

def es_administrador_supabase(usuario):
    """Verifica si el usuario es administrador según datos de Supabase"""
    if not usuario:
        return False
    
    # Verificar rol de admin
    if usuario.get("rol") == "admin":
        return True
    
    # Verificar flags de supervisor
    if usuario.get("es_supervisor") or usuario.get("es_supervisor_tareas"):
        return True
    
    # Verificar módulos con permisos de admin
    modulos = usuario.get("modulos", {})
    if isinstance(modulos, dict):
        for modulo, permisos in modulos.items():
            if isinstance(permisos, dict) and permisos.get("admin", False):
                return True
    
    return False
