#!/usr/bin/env python3
"""
🔑 Sistema de Login Simple para Testing y Desarrollo
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps

# Crear blueprint para login simple
simple_login_bp = Blueprint("simple_login", __name__)

# Usuarios de prueba (en producción esto vendría de la base de datos)
USUARIOS_PRUEBA = {
    "admin@test.com": {
        "password": "123456",
        "tipo": "admin",
        "nombre": "Admin Test",
        "nombre_nora": "aura",
        "is_admin": True
    },
    "cliente@test.com": {
        "password": "123456", 
        "tipo": "cliente",
        "nombre": "Cliente Test",
        "nombre_nora": "aura",
        "is_admin": False
    },
    "aura@test.com": {
        "password": "123456",
        "tipo": "cliente", 
        "nombre": "Cliente Aura",
        "nombre_nora": "aura",
        "is_admin": False
    }
}

@simple_login_bp.route("/simple")
def login_simple():
    """Página de login simple para testing"""
    return render_template("login_simple.html")

@simple_login_bp.route("/simple/auth", methods=["POST"])
def auth_simple():
    """Autenticación simple para testing"""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    
    if not email or not password:
        flash("Email y contraseña son obligatorios", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Verificar credenciales
    usuario = USUARIOS_PRUEBA.get(email)
    if not usuario or usuario["password"] != password:
        flash("Credenciales incorrectas", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Establecer sesión con configuración explícita
    session.permanent = True  # Hacer la sesión permanente
    session["email"] = email
    session["name"] = usuario["nombre"]
    session["nombre_nora"] = usuario["nombre_nora"]
    session["is_admin"] = usuario["is_admin"]
    session["user"] = {
        "id": f"test-{email}",
        "email": email,
        "nombre": usuario["nombre"],
        "nombre_nora": usuario["nombre_nora"],
        "tipo": usuario["tipo"]
    }
    
    # Forzar que la sesión se guarde
    session.modified = True
    
    print(f"🔐 Sesión establecida para {email}")
    print(f"📊 Session keys: {list(session.keys())}")
    
    flash(f"✅ Bienvenido {usuario['nombre']}", "success")
    
    # Redirigir según el tipo de usuario
    if usuario["is_admin"]:
        return redirect("/admin")
    else:
        return redirect(f"/panel_cliente/{usuario['nombre_nora']}/entrenar")

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
    """Endpoint para debug de sesión"""
    return jsonify({
        "session_data": dict(session),
        "logged_in": bool(session.get("email")),
        "is_admin": session.get("is_admin", False),
        "nombre_nora": session.get("nombre_nora")
    })
