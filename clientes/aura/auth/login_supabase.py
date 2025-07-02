"""
🔑 Sistema de Login con Supabase - AuraAI2
- Autenticación segura con Supabase
- Modo desarrollo solo en localhost
- Gestión de sesiones mejorada
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.auth_supabase import (
    verificar_usuario_supabase, 
    establecer_sesion_supabase, 
    es_localhost, 
    es_desarrollo
)

# Crear blueprint para login con Supabase
login_supabase_bp = Blueprint("login_supabase", __name__)

@login_supabase_bp.route("/")
def login_principal():
    """Página principal de login"""
    # Si ya está autenticado, redirigir
    if session.get("email"):
        if session.get("is_admin"):
            return redirect("/admin")
        else:
            nombre_nora = session.get("nombre_nora", "aura")
            return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
    
    # Mostrar página de login
    return render_template("login_supabase.html", 
                         es_localhost=es_localhost(),
                         es_desarrollo=es_desarrollo())

@login_supabase_bp.route("/auth", methods=["POST"])
def autenticar():
    """Autenticación con email/password usando Supabase"""
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    
    if not email or not password:
        flash("Email y contraseña son obligatorios", "error")
        return redirect(url_for("login_supabase.login_principal"))
    
    try:
        # Verificar usuario en Supabase
        usuario = verificar_usuario_supabase(email)
        if not usuario:
            flash("Usuario no encontrado o inactivo", "error")
            return redirect(url_for("login_supabase.login_principal"))
        
        # Verificar contraseña (si existe)
        password_bd = usuario.get("password")
        if password_bd:
            # Hash simple para comparar (mejorar en producción con bcrypt)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash != password_bd:
                flash("Contraseña incorrecta", "error")
                return redirect(url_for("login_supabase.login_principal"))
        else:
            flash("Usuario sin contraseña configurada. Contacte al administrador.", "error")
            return redirect(url_for("login_supabase.login_principal"))
        
        # Establecer sesión
        establecer_sesion_supabase(usuario)
        
        flash(f"✅ Bienvenido {usuario['nombre']}", "success")
        
        # Redirigir según permisos
        if session.get("is_admin"):
            return redirect("/admin")
        else:
            nombre_nora = usuario.get("nombre_nora", "aura")
            return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
    
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        flash("Error interno del sistema", "error")
        return redirect(url_for("login_supabase.login_principal"))

@login_supabase_bp.route("/dev", methods=["GET", "POST"])
def login_desarrollo():
    """Login de desarrollo - SOLO funciona en localhost"""
    if not es_localhost():
        flash("Acceso denegado: Login de desarrollo solo disponible en localhost", "error")
        return redirect(url_for("login_supabase.login_principal"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        
        if not email:
            flash("Email es obligatorio", "error")
            return redirect(url_for("login_supabase.login_desarrollo"))
        
        try:
            # Verificar si existe en Supabase
            usuario = verificar_usuario_supabase(email)
            if usuario:
                # Usuario existe, establecer sesión real
                establecer_sesion_supabase(usuario)
                flash(f"✅ Modo desarrollo: Sesión establecida para {usuario['nombre']}", "success")
            else:
                # Usuario no existe, crear sesión temporal de desarrollo
                session["email"] = email
                session["name"] = f"Dev User ({email})"
                session["nombre_nora"] = "aura"
                session["is_admin"] = True
                session["user"] = {
                    "id": "dev-temp-id",
                    "email": email,
                    "nombre": f"Dev User ({email})",
                    "nombre_nora": "aura",
                    "rol": "admin"
                }
                session.permanent = True
                flash(f"🔧 Modo desarrollo: Sesión temporal creada para {email}", "warning")
            
            # Redirigir según permisos
            if session.get("is_admin"):
                return redirect("/admin")
            else:
                nombre_nora = session.get("nombre_nora", "aura")
                return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
                
        except Exception as e:
            print(f"❌ Error en login de desarrollo: {e}")
            flash("Error en login de desarrollo", "error")
            return redirect(url_for("login_supabase.login_desarrollo"))
    
    return render_template("login_desarrollo.html")

@login_supabase_bp.route("/google")
def login_google():
    """Iniciar login con Google OAuth (pendiente implementación)"""
    flash("Login con Google en desarrollo", "info")
    return redirect(url_for("login_supabase.login_principal"))

@login_supabase_bp.route("/logout")
def logout():
    """Cerrar sesión"""
    user_name = session.get("name", "Usuario")
    session.clear()
    flash(f"✅ Sesión cerrada para {user_name}", "success")
    return redirect(url_for("login_supabase.login_principal"))

@login_supabase_bp.route("/status")
def status():
    """API para verificar estado de login"""
    if session.get("email"):
        return jsonify({
            "logged_in": True,
            "user": session.get("user", {}),
            "is_admin": session.get("is_admin", False),
            "nombre_nora": session.get("nombre_nora"),
            "es_localhost": es_localhost(),
            "es_desarrollo": es_desarrollo()
        })
    else:
        return jsonify({
            "logged_in": False,
            "es_localhost": es_localhost(),
            "es_desarrollo": es_desarrollo()
        })

@login_supabase_bp.route("/test")
def test_conexion():
    """Endpoint para probar la conexión con Supabase"""
    if not es_localhost():
        return jsonify({"error": "Acceso denegado"}), 403
    
    try:
        # Probar conexión con Supabase
        response = supabase.table("usuarios_clientes").select("correo, nombre").limit(1).execute()
        
        return jsonify({
            "success": True,
            "message": "Conexión con Supabase exitosa",
            "data": response.data,
            "es_localhost": es_localhost(),
            "es_desarrollo": es_desarrollo()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error conectando con Supabase"
        }), 500
