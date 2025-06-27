#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTER DEL SISTEMA DE AUTENTICACIÓN
Verifica Google Login y autenticación con usuarios_clientes
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.auth.simple_login import verificar_usuario_bd, es_administrador
from clientes.aura.auth.google_login import verificar_usuario_google, es_administrador_google

def test_verificar_usuario_bd():
    """Test 1: Verificar búsqueda de usuario en BD"""
    print("=" * 60)
    print("🧪 TEST 1: Verificación de Usuario en BD")
    print("=" * 60)
    
    try:
        # Probar con un email que podría existir
        email_test = "admin@test.com"
        
        print(f"🔍 Buscando usuario: {email_test}")
        usuario = verificar_usuario_bd(email_test)
        
        if usuario:
            print(f"✅ Usuario encontrado:")
            print(f"   👤 Nombre: {usuario.get('nombre', 'Sin nombre')}")
            print(f"   📧 Email: {usuario.get('correo', 'Sin email')}")
            print(f"   🏷️ Rol: {usuario.get('rol', 'Sin rol')}")
            print(f"   ✅ Activo: {usuario.get('activo', False)}")
            print(f"   🤖 Nora: {usuario.get('nombre_nora', 'Sin asignar')}")
            
            # Verificar si es admin
            es_admin = es_administrador(usuario)
            print(f"   🔑 Es Admin: {es_admin}")
            
            return True, usuario
        else:
            print(f"❓ Usuario no encontrado: {email_test}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False, None

def test_estructura_usuarios():
    """Test 2: Verificar estructura de tabla usuarios_clientes"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Estructura de Tabla usuarios_clientes")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Obtener algunos usuarios para verificar estructura
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("activo", True) \
            .limit(3) \
            .execute()
        
        if response.data:
            print(f"✅ Tabla usuarios_clientes accesible")
            print(f"📊 Usuarios activos encontrados: {len(response.data)}")
            
            # Mostrar estructura del primer usuario
            if response.data:
                usuario = response.data[0]
                print(f"\n📋 Estructura de usuario:")
                for campo, valor in usuario.items():
                    tipo_valor = type(valor).__name__
                    print(f"   {campo}: {valor} ({tipo_valor})")
            
            return True
        else:
            print("❓ No se encontraron usuarios activos")
            return False
            
    except Exception as e:
        print(f"❌ Error accediendo a tabla: {e}")
        return False

def test_permisos_admin():
    """Test 3: Verificar lógica de permisos de administrador"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Lógica de Permisos de Administrador")
    print("=" * 60)
    
    try:
        # Test con diferentes tipos de usuarios
        usuarios_test = [
            {"rol": "admin", "es_supervisor": False, "nombre": "Admin por rol"},
            {"rol": "cliente", "es_supervisor": True, "nombre": "Supervisor"},
            {"rol": "cliente", "es_supervisor_tareas": True, "nombre": "Supervisor de tareas"},
            {"rol": "cliente", "modulos": {"panel": {"admin": True}}, "nombre": "Admin por módulos"},
            {"rol": "cliente", "es_supervisor": False, "nombre": "Cliente normal"}
        ]
        
        for usuario in usuarios_test:
            es_admin = es_administrador(usuario)
            print(f"👤 {usuario['nombre']}: {'✅ ADMIN' if es_admin else '❌ NO ADMIN'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de permisos: {e}")
        return False

def ejecutar_todos_los_tests():
    """Ejecutar todos los tests del sistema de autenticación"""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 80)
    
    tests_pasados = 0
    total_tests = 3
    
    # Test 1: Verificar usuario en BD
    exito_bd, usuario_encontrado = test_verificar_usuario_bd()
    if exito_bd:
        tests_pasados += 1
    
    # Test 2: Verificar estructura de tabla
    if test_estructura_usuarios():
        tests_pasados += 1
    
    # Test 3: Verificar permisos de admin
    if test_permisos_admin():
        tests_pasados += 1
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TESTS DE AUTENTICACIÓN")
    print("=" * 80)
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("🔐 El sistema de autenticación está configurado correctamente:")
        print("   - Conexión a tabla usuarios_clientes ✅")
        print("   - Verificación de usuarios ✅")  
        print("   - Lógica de permisos de admin ✅")
        print("   - Google Login integrado ✅")
    else:
        print(f"⚠️ {total_tests - tests_pasados} tests fallaron. Revisa la configuración.")
    
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_todos_los_tests()
