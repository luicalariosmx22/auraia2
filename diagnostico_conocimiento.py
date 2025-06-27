#!/usr/bin/env python3
"""
🔍 Diagnóstico Completo - Bloques de Conocimiento
Este script identifica por qué no funcionan los bloques de conocimiento
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_environment():
    """Verificar variables de entorno"""
    print("🔧 VERIFICANDO VARIABLES DE ENTORNO")
    print("=" * 50)
    
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20} (configurada)")
        else:
            print(f"❌ {var}: NO CONFIGURADA")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_supabase_connection():
    """Verificar conexión directa a Supabase"""
    print("\n🗄️ VERIFICANDO CONEXIÓN A SUPABASE")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Variables de Supabase no configuradas")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente Supabase creado exitosamente")
        
        # Probar consulta a conocimiento_nora
        print("🔍 Probando consulta a tabla 'conocimiento_nora'...")
        res = supabase.table("conocimiento_nora").select("*").limit(1).execute()
        print(f"✅ Consulta exitosa - Registros encontrados: {len(res.data)}")
        
        # Verificar estructura de la tabla
        if res.data:
            print("📋 Estructura del primer registro:")
            print(json.dumps(res.data[0], indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_server_endpoints():
    """Verificar endpoints del servidor Flask"""
    print("\n🌐 VERIFICANDO ENDPOINTS DEL SERVIDOR")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    nombre_nora = "aura"
    
    endpoints_to_test = [
        f"/panel_cliente/{nombre_nora}/entrenar/bloques",
        f"/panel_cliente/{nombre_nora}/entrenamiento",
        f"/debug_info"
    ]
    
    server_running = False
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"🔍 Probando: {url}")
        
        try:
            if endpoint == "/debug_info":
                response = requests.get(url, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                server_running = True
                if endpoint == "/debug_info":
                    try:
                        data = response.json()
                        print(f"   ✅ Blueprints registrados: {len(data.get('blueprints_registrados', []))}")
                        print(f"   ✅ Rutas registradas: {len(data.get('rutas_registradas', []))}")
                        
                        # Buscar rutas de conocimiento
                        rutas = data.get('rutas_registradas', [])
                        rutas_conocimiento = [r for r in rutas if 'bloques' in r]
                        if rutas_conocimiento:
                            print(f"   ✅ Rutas de bloques encontradas: {rutas_conocimiento}")
                        else:
                            print(f"   ❌ NO se encontraron rutas de bloques")
                    except:
                        print(f"   ⚠️ Respuesta no es JSON válido")
                else:
                    print(f"   ✅ Endpoint accesible")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Servidor no disponible en {base_url}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return server_running

def check_blueprint_registration():
    """Verificar si el blueprint está registrado correctamente"""
    print("\n📋 VERIFICANDO REGISTRO DE BLUEPRINT")
    print("=" * 50)
    
    try:
        # Leer el archivo de inicialización
        init_file = "clientes/aura/__init__.py"
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar registro de cliente_nora_bp
        if "cliente_nora_bp" in content:
            print("✅ Blueprint 'cliente_nora_bp' encontrado en __init__.py")
        else:
            print("❌ Blueprint 'cliente_nora_bp' NO encontrado en __init__.py")
        
        # Buscar safe_register_blueprint
        if "safe_register_blueprint(app, cliente_nora_bp" in content:
            print("✅ Registro del blueprint encontrado")
        else:
            print("❌ Registro del blueprint NO encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo archivo de inicialización: {e}")
        return False

def test_specific_endpoint():
    """Test específico del endpoint de bloques"""
    print("\n🎯 TEST ESPECÍFICO - ENDPOINT BLOQUES")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    nombre_nora = "aura"
    
    # Test GET
    url_get = f"{base_url}/panel_cliente/{nombre_nora}/entrenar/bloques"
    print(f"🔍 GET {url_get}")
    
    try:
        response = requests.get(url_get, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   ⚠️ Response (no JSON): {response.text}")
        else:
            print(f"   ❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Función principal de diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO - BLOQUES DE CONOCIMIENTO")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    env_ok = check_environment()
    
    # 2. Verificar conexión a Supabase
    if env_ok:
        supabase_ok = check_supabase_connection()
    else:
        supabase_ok = False
        print("⏭️ Saltando test de Supabase (variables no configuradas)")
    
    # 3. Verificar servidor Flask
    server_ok = check_server_endpoints()
    
    # 4. Verificar registro de blueprint
    blueprint_ok = check_blueprint_registration()
    
    # 5. Test específico si el servidor está corriendo
    if server_ok:
        test_specific_endpoint()
    
    # Resumen final
    print("\n📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    print(f"Variables de entorno: {'✅' if env_ok else '❌'}")
    print(f"Conexión Supabase:    {'✅' if supabase_ok else '❌'}")
    print(f"Servidor Flask:       {'✅' if server_ok else '❌'}")
    print(f"Blueprint registrado: {'✅' if blueprint_ok else '❌'}")
    
    if not server_ok:
        print("\n🚨 ACCIÓN REQUERIDA:")
        print("1. Inicia el servidor con: source railway_session.sh && start_server")
        print("2. Luego ejecuta este script nuevamente")
    elif not env_ok or not supabase_ok:
        print("\n🚨 PROBLEMA DE CONFIGURACIÓN:")
        print("Revisa las variables de entorno en .env.local")
    elif not blueprint_ok:
        print("\n🚨 PROBLEMA DE REGISTRO:")
        print("El blueprint no está registrado correctamente")
    else:
        print("\n🎉 TODO PARECE ESTAR BIEN!")
        print("Si aún no funciona, puede ser un problema de autenticación/sesión")

if __name__ == "__main__":
    main()
