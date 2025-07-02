#!/usr/bin/env python3
"""
🌐 Rutas Flask para Autenticación con Supabase
Maneja todas las rutas de login, registro, logout, etc.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import json
from supabase_auth import crear_auth_supabase

# Crear Blueprint para autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Crear instancia de autenticación
auth_supabase = crear_auth_supabase()

def login_requerido(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user_authenticated'):
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def solo_admin(f):
    """Decorador para rutas que solo pueden acceder administradores"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user_authenticated'):
            flash('Debes iniciar sesión', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('user_role') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('auth.dashboard'))
        
        return f(*args, **kwargs)
    return wrapper

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Email y contraseña son requeridos', 'error')
                return render_template('auth/login.html')
            
            if not auth_supabase:
                flash('Error de configuración del sistema', 'error')
                return render_template('auth/login.html')
            
            # Intentar login
            exito, mensaje, datos = auth_supabase.sign_in(email, password)
            
            if exito:
                # Guardar datos en sesión
                session['user_authenticated'] = True
                session['user_id'] = datos.get('user_id')
                session['user_email'] = datos.get('email')
                session['access_token'] = datos.get('access_token')
                session['user_metadata'] = datos.get('user_metadata', {})
                
                # Determinar rol del usuario
                metadata = datos.get('user_metadata', {})
                session['user_role'] = metadata.get('role', 'user')
                session['user_name'] = metadata.get('nombre', email.split('@')[0])
                
                flash(f'¡Bienvenido {session["user_name"]}!', 'success')
                
                # Redirigir según el rol
                if session['user_role'] == 'admin':
                    return redirect(url_for('auth.admin_dashboard'))
                else:
                    return redirect(url_for('auth.dashboard'))
            else:
                flash(mensaje, 'error')
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            flash('Error interno del servidor', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            nombre = request.form.get('nombre', '').strip()
            telefono = request.form.get('telefono', '').strip()
            
            # Validaciones
            if not all([email, password, confirm_password, nombre]):
                flash('Todos los campos son requeridos', 'error')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('auth/register.html')
            
            if len(password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres', 'error')
                return render_template('auth/register.html')
            
            if not auth_supabase:
                flash('Error de configuración del sistema', 'error')
                return render_template('auth/register.html')
            
            # Metadata del usuario
            user_metadata = {
                'nombre': nombre,
                'telefono': telefono,
                'role': 'user',  # Por defecto usuario normal
                'created_via': 'web_registration'
            }
            
            # Intentar registro
            exito, mensaje, datos = auth_supabase.sign_up(email, password, user_metadata)
            
            if exito:
                flash('¡Registro exitoso! Revisa tu email para confirmar tu cuenta.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(mensaje, 'error')
                
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            flash('Error interno del servidor', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    try:
        if auth_supabase:
            auth_supabase.sign_out()
        
        # Limpiar sesión
        session.clear()
        flash('Sesión cerrada exitosamente', 'success')
        
    except Exception as e:
        print(f"❌ Error en logout: {e}")
        flash('Error cerrando sesión', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_requerido
def dashboard():
    """Dashboard principal del usuario"""
    user_data = {
        'name': session.get('user_name', 'Usuario'),
        'email': session.get('user_email'),
        'role': session.get('user_role', 'user'),
        'metadata': session.get('user_metadata', {})
    }
    return render_template('auth/dashboard.html', user=user_data)

@auth_bp.route('/admin')
@solo_admin
def admin_dashboard():
    """Dashboard de administrador"""
    user_data = {
        'name': session.get('user_name', 'Admin'),
        'email': session.get('user_email'),
        'role': session.get('user_role'),
        'metadata': session.get('user_metadata', {})
    }
    return render_template('auth/admin_dashboard.html', user=user_data)

@auth_bp.route('/profile')
@login_requerido
def profile():
    """Perfil del usuario"""
    user_data = {
        'name': session.get('user_name', 'Usuario'),
        'email': session.get('user_email'),
        'role': session.get('user_role', 'user'),
        'metadata': session.get('user_metadata', {}),
        'user_id': session.get('user_id')
    }
    return render_template('auth/profile.html', user=user_data)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Página para resetear contraseña"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            
            if not email:
                flash('Email es requerido', 'error')
                return render_template('auth/forgot_password.html')
            
            if not auth_supabase:
                flash('Error de configuración del sistema', 'error')
                return render_template('auth/forgot_password.html')
            
            # Enviar email de reset
            exito, mensaje = auth_supabase.reset_password(email)
            
            if exito:
                flash('Si el email existe, recibirás instrucciones para resetear tu contraseña', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(mensaje, 'error')
                
        except Exception as e:
            print(f"❌ Error en reset password: {e}")
            flash('Error interno del servidor', 'error')
    
    return render_template('auth/forgot_password.html')

# Rutas API para uso con JavaScript
@auth_bp.route('/api/user-info')
@login_requerido
def api_user_info():
    """API para obtener información del usuario actual"""
    try:
        user_data = {
            'user_id': session.get('user_id'),
            'email': session.get('user_email'),
            'name': session.get('user_name'),
            'role': session.get('user_role'),
            'metadata': session.get('user_metadata', {}),
            'authenticated': session.get('user_authenticated', False)
        }
        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@auth_bp.route('/api/check-auth')
def api_check_auth():
    """API para verificar si el usuario está autenticado"""
    return jsonify({
        'authenticated': session.get('user_authenticated', False),
        'user_id': session.get('user_id'),
        'role': session.get('user_role', 'user')
    })

# Contexto global para templates
@auth_bp.context_processor
def inject_auth_context():
    """Inyectar datos de autenticación en todos los templates"""
    return {
        'user_authenticated': session.get('user_authenticated', False),
        'user_name': session.get('user_name', ''),
        'user_email': session.get('user_email', ''),
        'user_role': session.get('user_role', 'user'),
        'is_admin': session.get('user_role') == 'admin'
    }

# Manejador de errores
@auth_bp.errorhandler(403)
def forbidden(error):
    """Página de acceso denegado"""
    return render_template('auth/403.html'), 403

@auth_bp.errorhandler(404)
def not_found(error):
    """Página no encontrada"""
    return render_template('auth/404.html'), 404
