#!/usr/bin/env python3
"""
🔑 Sistema de Login Simple para Testing y Desarrollo
⚠️  ADVERTENCIA: Este sistema NO debe usarse en producción
📝 Implementar autenticación segura con hash de contraseñas antes de deployment
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.google_login import google_login_bp
import hashlib

# Crear blueprint para login simple
simple_login_bp = Blueprint("simple_login", __name__)

# Autenticación a través de base de datos segura y Google OAuth

def verificar_usuario_bd(email):
    """
    Verifica si el usuario existe en la tabla usuarios_clientes
    """
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("correo", email) \
            .eq("activo", True) \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"✅ Usuario encontrado en BD: {usuario['nombre']}")
            return usuario
        else:
            print(f"❌ Usuario no encontrado en BD: {email}")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando usuario: {e}")
        return None

def es_administrador(usuario):
    """
    Verifica si el usuario es administrador basado en rol y permisos
    """
    if not usuario:
        return False
    
    # Verificar rol de admin o supervisor
    if usuario.get("rol") == "admin":
        return True
    
    if usuario.get("es_supervisor") or usuario.get("es_supervisor_tareas"):
        return True
    
    # Verificar módulos con permisos de admin
    modulos = usuario.get("modulos", {})
    if isinstance(modulos, dict):
        for modulo, permisos in modulos.items():
            if isinstance(permisos, dict) and permisos.get("admin", False):
                return True
    
    return False

@simple_login_bp.route("/google/login")
def google_login():
    """Redirigir a Google OAuth"""
    return redirect(url_for("google_login.login"))

@simple_login_bp.route("/simple")
def login_simple():
    """Página de login simple para testing"""
    return render_template("login_simple.html")

@simple_login_bp.route("/simple/auth", methods=["POST"])
def auth_simple():
    """Autenticación con email/password contra base de datos"""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    
    if not email or not password:
        flash("Email y contraseña son obligatorios", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Verificar usuario en base de datos
    usuario = verificar_usuario_bd(email)
    if not usuario:
        flash("Usuario no encontrado o inactivo", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Verificar contraseña (si existe en BD)
    password_bd = usuario.get("password")
    if password_bd:
        # Hash simple para comparar (en producción usar bcrypt)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != password_bd:
            flash("Contraseña incorrecta", "error")
            return redirect(url_for("simple_login.login_simple"))
    else:
        flash("Usuario sin contraseña configurada. Use Google Login.", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Establecer sesión
    establecer_sesion_usuario(usuario)
    
    flash(f"✅ Bienvenido {usuario['nombre']}", "success")
    
    # Redirigir según permisos
    if es_administrador(usuario):
        return redirect("/admin")
    else:
        nombre_nora = usuario.get("nombre_nora", "aura")
        return redirect(f"/panel_cliente/{nombre_nora}/entrenar")

@simple_login_bp.route("/google/callback")
def google_callback():
    """Callback de Google OAuth"""
    # Obtener email del token de Google (implementar según tu sistema OAuth)
    email = request.args.get("email")  # Temporal - implementar OAuth real
    
    if not email:
        flash("Error en autenticación con Google", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Verificar usuario en base de datos
    usuario = verificar_usuario_bd(email)
    if not usuario:
        flash("Usuario no autorizado en el sistema", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Establecer sesión
    establecer_sesion_usuario(usuario)
    
    flash(f"✅ Bienvenido {usuario['nombre']} (Google)", "success")
    
    # Redirigir según permisos
    if es_administrador(usuario):
        return redirect("/admin")
    else:
        nombre_nora = usuario.get("nombre_nora", "aura")
        return redirect(f"/panel_cliente/{nombre_nora}/entrenar")

def establecer_sesion_usuario(usuario):
    """Establece la sesión del usuario autenticado"""
    session.permanent = True
    session["email"] = usuario["correo"]
    session["name"] = usuario["nombre"]
    session["nombre_nora"] = usuario.get("nombre_nora", "aura")
    session["is_admin"] = es_administrador(usuario)
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
    
    print(f"🔐 Sesión establecida para {usuario['correo']}")
    print(f"📊 Permisos: Admin={es_administrador(usuario)}, Rol={usuario.get('rol')}")

@simple_login_bp.route("/logout")
def logout_simple():
    """Cerrar sesión"""
    session.clear()
    flash("✅ Sesión cerrada correctamente", "success")
    return redirect(url_for("simple_login.login_simple"))

@simple_login_bp.route("/status")
def login_status():
    """API para verificar estado de login"""
    if session.get("email"):
        return jsonify({
            "logged_in": True,
            "user": session.get("user", {}),
            "is_admin": session.get("is_admin", False),
            "nombre_nora": session.get("nombre_nora")
        })
    else:
        return jsonify({"logged_in": False})

def require_login_simple(f):
    """Decorador simple para requerir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("email"):
            flash("Debes iniciar sesión para acceder", "error")
            return redirect(url_for("simple_login.login_simple"))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# 🎯 RUTAS DE REDIRECT PRINCIPALES
# ============================================

@simple_login_bp.route("/")
def login_redirect():
    """Redirect / a login simple"""
    return redirect(url_for("simple_login.login_simple"))

@simple_login_bp.route("/login")
def login_legacy():
    """Redirect /login a login simple"""
    return redirect(url_for("simple_login.login_simple"))

@simple_login_bp.route("/panel")
def panel_redirect():
    """Redirect /panel a login si no está autenticado"""
    if session.get("email"):
        nombre_nora = session.get("nombre_nora", "aura")
        return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
    else:
        return redirect(url_for("simple_login.login_simple"))

@simple_login_bp.route("/admin")
def admin_redirect():
    """Redirect /admin a login si no está autenticado"""
    if session.get("email") and session.get("is_admin"):
        return redirect("/admin/dashboard")
    else:
        flash("Acceso de administrador requerido", "error")
        return redirect(url_for("simple_login.login_simple"))

@simple_login_bp.route("/test-session")
def test_session():
    """Endpoint para debug de sesión - SOLO en localhost"""
    from clientes.aura.utils.auth_supabase import es_localhost
    
    # Solo permitir en localhost
    if not es_localhost():
        return jsonify({"error": "Acceso denegado"}), 403
    
    return jsonify({
        "session_data": dict(session),
        "logged_in": bool(session.get("email")),
        "is_admin": session.get("is_admin", False),
        "nombre_nora": session.get("nombre_nora")
    })

@simple_login_bp.route("/login_supabase")
def login_supabase():
    """Redirigir a la nueva página de login con Supabase"""
    # Si ya está autenticado, redirigir
    if session.get("email"):
        if session.get("is_admin"):
            return redirect("/admin")
        else:
            nombre_nora = session.get("nombre_nora", "aura")
            return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
    
    # Mostrar página de login
    return render_template("login_supabase.html")

@simple_login_bp.route("/dev/activate")
def activate_dev_mode():
    """Activar modo desarrollo solo en localhost"""
    from clientes.aura.utils.auth_supabase import es_localhost
    
    # SOLO permitir en localhost
    if not es_localhost():
        flash("Acceso denegado", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Verificar que sea realmente localhost
    if request.host.lower() not in ['localhost:5000', '127.0.0.1:5000', '0.0.0.0:5000']:
        flash("Acceso denegado", "error") 
        return redirect(url_for("simple_login.login_simple"))
    
    # Establecer sesión de desarrollo SOLO en localhost
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
    
    flash("✅ Modo desarrollo activado", "success")
    return redirect("/admin")
