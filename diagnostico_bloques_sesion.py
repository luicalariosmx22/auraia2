#!/usr/bin/env python3
"""
Script para diagnosticar directamente el problema con los bloques de conocimiento
y verificar si es un problema de sesión o del endpoint
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from dotenv import load_dotenv
from flask import Flask, session
from clientes.aura.utils.login_required import login_required_cliente

# Cargar configuración
load_dotenv(".env.local")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_directo_bloques():
    """Test directo del endpoint de bloques sin servidor"""
    print("🔄 Testando bloques directamente...")
    
    try:
        # Test directo a la base de datos
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", "aura") \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        print(f"✅ Query directa exitosa")
        print(f"📊 Encontrados {len(res.data)} bloques")
        
        if res.data:
            print(f"🔍 Ejemplo de bloque:")
            for i, bloque in enumerate(res.data[:2]):
                print(f"  {i+1}. ID: {bloque.get('id', 'N/A')}")
                print(f"     Contenido: {bloque.get('contenido', 'N/A')[:100]}...")
                print(f"     Activo: {bloque.get('activo', 'N/A')}")
                print(f"     Fecha: {bloque.get('fecha_creacion', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en query directa: {e}")
        return False

def test_decorador_login():
    """Test del decorador de login"""
    print("\n🔄 Testando decorador de login...")
    
    # Crear una app Flask mínima para test
    app = Flask(__name__)
    app.secret_key = "test_key"
    
    @app.route("/test")
    @login_required_cliente
    def test_route():
        return {"success": True, "message": "Login requerido funcionando"}
    
    with app.test_client() as client:
        with app.test_request_context():
            # Test sin sesión
            response = client.get("/test")
            print(f"Sin sesión - Status: {response.status_code}")
            
            # Test con sesión
            with client.session_transaction() as sess:
                sess['cliente_logueado'] = True
                sess['cliente_usuario'] = 'admin'
            
            response = client.get("/test")
            print(f"Con sesión - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Decorador funcionando correctamente")
            else:
                print("❌ Problema con decorador")

def verificar_configuracion_sesion():
    """Verificar la configuración de sesión en el sistema"""
    print("\n🔄 Verificando configuración de sesión...")
    
    # Verificar archivos de configuración
    archivos_clave = [
        "clientes/aura/utils/login_required.py",
        "clientes/aura/auth/simple_login.py"
    ]
    
    for archivo in archivos_clave:
        ruta_completa = os.path.join(os.path.dirname(__file__), archivo)
        if os.path.exists(ruta_completa):
            print(f"✅ {archivo} existe")
        else:
            print(f"❌ {archivo} NO existe")

def main():
    print("🚀 Iniciando diagnóstico completo de bloques de conocimiento\n")
    
    # Test 1: Query directa a BD
    test_directo_bloques()
    
    # Test 2: Decorador de login
    test_decorador_login()
    
    # Test 3: Configuración
    verificar_configuracion_sesion()
    
    print("\n📝 RESUMEN:")
    print("- Si la query directa funciona pero el endpoint no, es problema de sesión")
    print("- Si el decorador falla, es problema de configuración de Flask")
    print("- Si todo funciona aquí, el problema está en el frontend o en cookies")

if __name__ == "__main__":
    main()
