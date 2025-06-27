#!/usr/bin/env python3
"""
🔍 Diagnóstico completo de problemas con bloques de conocimiento
- Verifica autenticación
- Comprueba endpoints
- Valida base de datos
- Simula frontend
"""

import requests
import json
import time

def verificar_servidor():
    """Verificar que el servidor está corriendo"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Servidor Flask está corriendo")
        return True
    except:
        print("❌ Servidor Flask NO está corriendo")
        print("   💡 Ejecuta: python run.py")
        return False

def test_endpoint_sin_auth():
    """Test del endpoint temporal sin autenticación"""
    print("\n🔓 Test endpoint temporal (sin autenticación):")
    try:
        url = "http://localhost:5000/test/bloques/test"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            if "bloques" in response.text.lower():
                print("   ✅ Endpoint temporal funciona")
                return True
            else:
                print("   ⚠️  Endpoint responde pero sin datos de bloques")
                return False
        else:
            print(f"   ❌ Error en endpoint temporal: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_endpoint_con_auth():
    """Test del endpoint principal con autenticación"""
    print("\n🔒 Test endpoint principal (requiere autenticación):")
    try:
        url = "http://localhost:5000/panel_cliente/test/entrenar/bloques"
        response = requests.get(url, allow_redirects=False, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if '/login' in location:
                print("   ✅ Correctamente redirige a login (requiere autenticación)")
                return True
            else:
                print(f"   ⚠️  Redirige a: {location}")
                return False
        elif response.status_code == 401:
            print("   ✅ Retorna 401 Unauthorized")
            return True
        else:
            print(f"   ❌ No requiere autenticación (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_endpoint_dev():
    """Test del endpoint de desarrollo"""
    print("\n🔧 Test endpoint de desarrollo (simula sesión):")
    try:
        url = "http://localhost:5000/dev/entrenar/test"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            if "admin_nora_entrenar" in response.text or "bloques" in response.text.lower():
                print("   ✅ Endpoint de desarrollo funciona")
                return True
            else:
                print("   ⚠️  Endpoint responde pero contenido inválido")
                return False
        else:
            print(f"   ❌ Error en endpoint de desarrollo: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_api_directa():
    """Test directo de la API usando sesión simulada"""
    print("\n🎯 Test API con sesión simulada:")
    try:
        # Primero, establecer sesión en /dev/entrenar/test
        session = requests.Session()
        
        # Establecer sesión
        url_session = "http://localhost:5000/dev/entrenar/test"
        response = session.get(url_session)
        print(f"   Estableciendo sesión: {response.status_code}")
        
        if response.status_code != 200:
            print("   ❌ No se pudo establecer sesión simulada")
            return False
        
        # Ahora intentar acceder al endpoint de bloques usando la misma sesión
        url_api = "http://localhost:5000/panel_cliente/test/entrenar/bloques"
        response = session.get(url_api)
        print(f"   API con sesión: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    bloques = data.get('data', [])
                    print(f"   ✅ API funciona - {len(bloques)} bloques encontrados")
                    if bloques:
                        print(f"      Primer bloque: {bloques[0].get('contenido', 'N/A')[:50]}...")
                    return True
                else:
                    print(f"   ❌ API error: {data.get('message', 'Unknown')}")
                    return False
            except:
                print("   ❌ Respuesta no es JSON válido")
                return False
        else:
            print(f"   ❌ API falló: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verificar_base_datos():
    """Verificar que hay datos en la base de datos"""
    print("\n💾 Verificando base de datos:")
    try:
        from supabase import create_client
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("   ❌ Variables de entorno de Supabase no configuradas")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Verificar tabla conocimiento_nora
        res = supabase.table("conocimiento_nora").select("*").limit(5).execute()
        print(f"   Total registros en conocimiento_nora: {len(res.data)}")
        
        # Verificar registros activos
        res_activos = supabase.table("conocimiento_nora").select("*").eq("activo", True).limit(5).execute()
        print(f"   Registros activos: {len(res_activos.data)}")
        
        # Verificar por nombre_nora = 'test'
        res_test = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", "test").eq("activo", True).execute()
        print(f"   Bloques para 'test': {len(res_test.data)}")
        
        if len(res_test.data) > 0:
            print(f"   ✅ Datos encontrados en BD")
            primer_bloque = res_test.data[0]
            print(f"      Ejemplo: {primer_bloque.get('contenido', 'N/A')[:50]}...")
            return True
        else:
            print("   ⚠️  No hay bloques para nombre_nora='test'")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando BD: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO COMPLETO DE BLOQUES DE CONOCIMIENTO")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Verificar servidor
    resultados['servidor'] = verificar_servidor()
    if not resultados['servidor']:
        print("\n❌ Servidor no está corriendo. No se pueden realizar más tests.")
        return
    
    # 2. Verificar base de datos
    resultados['base_datos'] = verificar_base_datos()
    
    # 3. Tests de endpoints
    resultados['endpoint_temporal'] = test_endpoint_sin_auth()
    resultados['endpoint_auth'] = test_endpoint_con_auth()
    resultados['endpoint_dev'] = test_endpoint_dev()
    resultados['api_sesion'] = test_api_directa()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    for test, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {test.replace('_', ' ').title()}: {'OK' if resultado else 'FALLO'}")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    
    if not resultados['base_datos']:
        print("🔹 Problema en base de datos:")
        print("   - Verificar variables de entorno SUPABASE_URL y SUPABASE_KEY")
        print("   - Crear algunos bloques de prueba")
        print("   - Ejecutar: python test_conocimiento_debug.py")
    
    if resultados['endpoint_temporal'] and not resultados['api_sesion']:
        print("🔹 Problema en autenticación:")
        print("   - Los endpoints principales están correctamente protegidos")
        print("   - Pero la sesión simulada no funciona correctamente")
        print("   - Verificar login_required_cliente en utils/")
    
    if resultados['api_sesion'] and resultados['base_datos']:
        print("🔹 Backend funciona correctamente:")
        print("   - El problema está en el frontend (JavaScript)")
        print("   - Verificar consola del navegador en /dev/entrenar/test")
        print("   - Asegurarse que el usuario esté logueado en el flujo real")
    
    print(f"\n🎯 Estado general: {'✅ FUNCIONANDO' if all(resultados.values()) else '⚠️ NECESITA CORRECCIÓN'}")

if __name__ == "__main__":
    main()
