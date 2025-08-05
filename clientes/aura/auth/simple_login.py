# =============================
# Lógica común para procesar login
# =============================
def procesar_login(usuario, origen=""):
    """
    Lógica común para procesar login (desde email o Google).
    """
    if not usuario:
        flash("Usuario no autorizado en el sistema", "error")
        return redirect(url_for("simple_login_unique.login_simple"))

    establecer_sesion_usuario(usuario)

    mensaje = f"Bienvenido {usuario['nombre']}"
    if origen:
        mensaje += f" ({origen})"
    flash(mensaje, "success")

    if es_administrador(usuario):
        return redirect("/admin")
    else:
        nombre_nora = usuario.get("nombre_nora", "aura")
        return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
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
import logging

logger = logging.getLogger(__name__)

# Crear blueprint para login simple
simple_login_bp = Blueprint("simple_login_unique", __name__, url_prefix='/login')

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
            return response.data[0]
        else:
            return None
    except Exception as e:
        logger.exception(f"Error al verificar usuario en la base de datos: {email}")
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

# Se eliminan funciones duplicadas de login para Google y logout
# Mantenemos solo las versiones principales y unificadas

@simple_login_bp.route("/simple", methods=["GET"])
def login_simple():
    return render_template("login_simple.html")

@simple_login_bp.route("/simple/auth", methods=["POST"])
def auth_simple():
    """Autenticación con email/password contra base de datos"""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    
    if not email or not password:
        flash("Email y contraseña son obligatorios", "error")
        return redirect(url_for("simple_login_unique.login_simple"))
    
    # Verificar usuario en base de datos
    usuario = verificar_usuario_bd(email)
    if not usuario:
        flash("Usuario no encontrado o inactivo", "error")
        return redirect(url_for("simple_login_unique.login_simple"))
    
    # Verificar contraseña (si existe en BD)
    password_bd = usuario.get("password")
    if password_bd:
        # Verificar si la contraseña en BD es un hash o texto plano
        if len(password_bd) == 64 and all(c in '0123456789abcdef' for c in password_bd.lower()):
            # Es un hash SHA256, comparar con hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            password_match = password_hash == password_bd
        else:
            # Es texto plano, comparar directamente
            password_match = password == password_bd
        
        if not password_match:
            flash("Contraseña incorrecta", "error")
            return redirect(url_for("simple_login_unique.login_simple"))
    else:
        flash("Usuario sin contraseña configurada. Use Google Login.", "error")
        return redirect(url_for("simple_login_unique.login_simple"))
    
    return procesar_login(usuario)

@simple_login_bp.route("/google/callback")
def google_callback():
    """Callback de Google OAuth"""
    # Obtener email del token de Google (implementar según tu sistema OAuth)
    email = request.args.get("email")  # Temporal - implementar OAuth real
    
    if not email:
        flash("Error en autenticación con Google", "error")
        return redirect(url_for("simple_login_unique.login_simple"))
    
    # Verificar usuario en base de datos
    usuario = verificar_usuario_bd(email)
    if not usuario:
        flash("Usuario no autorizado en el sistema", "error")
        return redirect(url_for("simple_login_unique.login_simple"))
    
    return procesar_login(usuario, origen="Google")

def establecer_sesion_usuario(usuario):
    """Establece la sesión del usuario autenticado"""
    try:
        session.permanent = True
        session["email"] = str(usuario["correo"])
        session["name"] = str(usuario["nombre"])
        session["nombre_nora"] = str(usuario.get("nombre_nora", "aura"))
        session["is_admin"] = bool(es_administrador(usuario))
        user_dict = {
            "id": str(usuario["id"]),
            "email": str(usuario["correo"]),
            "nombre": str(usuario["nombre"]),
            "nombre_nora": str(usuario.get("nombre_nora", "aura")),
            "rol": str(usuario.get("rol", "cliente")),
            "modulos": usuario.get("modulos", {}),
            "es_supervisor": bool(usuario.get("es_supervisor", False))
        }
        session["user"] = user_dict
        session.modified = True
        logger.info(f"✅ Sesión establecida para: {usuario['correo']}")
    except Exception as e:
        logger.exception("❌ Error al establecer sesión del usuario")

@simple_login_bp.route("/logout")
def logout_simple():
    """Cerrar sesión (ruta principal)"""
    try:
        if session:
            session.clear()
        flash("Sesión cerrada correctamente", "success")
        logger.info("✅ Sesión cerrada con éxito")
    except Exception as e:
        logger.exception("❌ Error al cerrar sesión")
        flash("Ocurrió un error al cerrar sesión", "error")
    return redirect(url_for("simple_login_unique.login_simple"))

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
            return redirect(url_for("simple_login_unique.login_simple"))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# 🎯 RUTAS DE REDIRECT PRINCIPALES
# ============================================

@simple_login_bp.route("/admin")
def admin_redirect():
    """Redirect /admin a login si no está autenticado"""
    if session.get("email") and session.get("is_admin"):
        return redirect("/admin/dashboard")
    else:
        flash("Acceso de administrador requerido", "error")
        return redirect(url_for("simple_login_unique.login_simple"))

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

# 🔥 Las siguientes funciones duplicadas han sido eliminadas:
# @simple_login_bp.route('/login')
# def login_main():
#     ...

# @simple_login_bp.route('/google')
# def google_oauth_redirect():
#     ...

# @simple_login_bp.route('/google/login')
# def google_login():
#     ...

# @simple_login_bp.route('/logout')
# def logout():
#     ...

# @simple_login_bp.route("/login_supabase")
# def login_supabase():
#     ...
