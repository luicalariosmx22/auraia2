#!/usr/bin/env python3
"""
🔐 Sistema de Autenticación con Supabase
Maneja login, registro, logout y verificación de usuarios
"""

from supabase import create_client, Client
from dotenv import load_dotenv
import os
from typing import Dict, Optional, Tuple
import json

# Cargar variables de entorno
load_dotenv()

class SupabaseAuth:
    """Clase para manejar autenticación con Supabase"""
    
    def __init__(self):
        """Inicializar cliente de Supabase"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ SUPABASE_URL y SUPABASE_KEY son requeridas en el archivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✅ Cliente Supabase inicializado correctamente")
    
    def sign_up(self, email: str, password: str, user_metadata: Dict = None) -> Tuple[bool, str, Dict]:
        """
        Registrar un nuevo usuario
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            user_metadata: Metadatos adicionales del usuario (nombre, teléfono, etc.)
        
        Returns:
            Tuple[bool, str, Dict]: (éxito, mensaje, datos_usuario)
        """
        try:
            print(f"🔐 Intentando registrar usuario: {email}")
            
            # Registrar usuario con Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if response.user:
                print(f"✅ Usuario registrado exitosamente: {email}")
                return True, "Usuario registrado exitosamente", {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "metadata": response.user.user_metadata
                }
            else:
                print(f"❌ Error en registro: Sin datos de usuario")
                return False, "Error en el registro", {}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error registrando usuario {email}: {error_msg}")
            return False, f"Error en registro: {error_msg}", {}
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Dict]:
        """
        Iniciar sesión con email y contraseña
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
        
        Returns:
            Tuple[bool, str, Dict]: (éxito, mensaje, datos_sesion)
        """
        try:
            print(f"🔐 Intentando login para: {email}")
            
            # Autenticar con Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                print(f"✅ Login exitoso para: {email}")
                return True, "Login exitoso", {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "user_metadata": response.user.user_metadata
                }
            else:
                print(f"❌ Login fallido: Credenciales inválidas")
                return False, "Credenciales inválidas", {}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error en login para {email}: {error_msg}")
            return False, f"Error en login: {error_msg}", {}
    
    def sign_out(self) -> Tuple[bool, str]:
        """
        Cerrar sesión del usuario actual
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            print("🔐 Cerrando sesión...")
            
            response = self.supabase.auth.sign_out()
            
            print("✅ Sesión cerrada exitosamente")
            return True, "Sesión cerrada exitosamente"
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error cerrando sesión: {error_msg}")
            return False, f"Error cerrando sesión: {error_msg}"
    
    def get_current_user(self) -> Tuple[bool, str, Dict]:
        """
        Obtener información del usuario actual
        
        Returns:
            Tuple[bool, str, Dict]: (éxito, mensaje, datos_usuario)
        """
        try:
            print("🔐 Obteniendo usuario actual...")
            
            user = self.supabase.auth.get_user()
            
            if user and user.user:
                print(f"✅ Usuario actual: {user.user.email}")
                return True, "Usuario obtenido", {
                    "user_id": user.user.id,
                    "email": user.user.email,
                    "user_metadata": user.user.user_metadata,
                    "created_at": user.user.created_at
                }
            else:
                print("❌ No hay usuario autenticado")
                return False, "No hay usuario autenticado", {}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error obteniendo usuario: {error_msg}")
            return False, f"Error obteniendo usuario: {error_msg}", {}
    
    def reset_password(self, email: str) -> Tuple[bool, str]:
        """
        Enviar email para resetear contraseña
        
        Args:
            email: Email del usuario
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            print(f"🔐 Enviando reset de contraseña a: {email}")
            
            response = self.supabase.auth.reset_password_email(email)
            
            print(f"✅ Email de reset enviado a: {email}")
            return True, "Email de reset enviado"
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error enviando reset a {email}: {error_msg}")
            return False, f"Error enviando reset: {error_msg}"
    
    def verify_token(self, token: str) -> Tuple[bool, str, Dict]:
        """
        Verificar un token de acceso
        
        Args:
            token: Token de acceso
        
        Returns:
            Tuple[bool, str, Dict]: (éxito, mensaje, datos_usuario)
        """
        try:
            print("🔐 Verificando token...")
            
            # Configurar el token para la sesión
            self.supabase.auth.set_session(token, token)  # Usar el mismo token como refresh
            
            user = self.supabase.auth.get_user()
            
            if user and user.user:
                print(f"✅ Token válido para: {user.user.email}")
                return True, "Token válido", {
                    "user_id": user.user.id,
                    "email": user.user.email,
                    "user_metadata": user.user.user_metadata
                }
            else:
                print("❌ Token inválido")
                return False, "Token inválido", {}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error verificando token: {error_msg}")
            return False, f"Error verificando token: {error_msg}", {}

# Función helper para crear instancia global
def crear_auth_supabase():
    """Crear instancia de autenticación Supabase"""
    try:
        return SupabaseAuth()
    except Exception as e:
        print(f"❌ Error creando SupabaseAuth: {e}")
        return None

# Test de la clase
def test_supabase_auth():
    """Test del sistema de autenticación"""
    print("=" * 70)
    print("🔐 TEST SISTEMA DE AUTENTICACIÓN SUPABASE")
    print("=" * 70)
    
    try:
        # Crear instancia
        auth = crear_auth_supabase()
        if not auth:
            print("❌ No se pudo crear la instancia de autenticación")
            return
        
        print("✅ Instancia de autenticación creada")
        
        # Test: Obtener usuario actual
        exito, mensaje, datos = auth.get_current_user()
        print(f"👤 Usuario actual: {mensaje}")
        if datos:
            print(f"   📧 Email: {datos.get('email')}")
            print(f"   🆔 ID: {datos.get('user_id')}")
        
        print()
        print("🧪 Para probar login/registro:")
        print("   auth.sign_up('test@example.com', 'password123', {'nombre': 'Test User'})")
        print("   auth.sign_in('test@example.com', 'password123')")
        print("   auth.sign_out()")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    test_supabase_auth()
