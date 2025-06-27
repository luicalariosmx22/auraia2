#!/usr/bin/env python3
"""
🔍 Test simple de bloques de conocimiento
"""

import requests

def test_simple():
    print("🔍 Test Rápido de Bloques")
    print("=" * 30)
    
    # Test 1: Endpoint temporal
    try:
        print("\n1. Test endpoint temporal:")
        response = requests.get("http://localhost:5000/test/bloques/test", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            if "bloques" in response.text.lower():
                print("   ✅ Endpoint temporal OK")
            else:
                print("   ⚠️ Sin datos de bloques")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Endpoint con auth (debe redirigir)
    try:
        print("\n2. Test endpoint con autenticación:")
        response = requests.get("http://localhost:5000/panel_cliente/test/entrenar/bloques", 
                              allow_redirects=False, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Requiere autenticación (redirige)")
        else:
            print("   ❌ No requiere autenticación")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Base de datos directa
    try:
        print("\n3. Test base de datos:")
        from supabase import create_client
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if SUPABASE_URL and SUPABASE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", "test").eq("activo", True).execute()
            print(f"   Bloques en BD: {len(res.data)}")
            if len(res.data) > 0:
                print("   ✅ Datos en BD OK")
            else:
                print("   ⚠️ No hay datos para 'test'")
        else:
            print("   ❌ Variables de entorno no configuradas")
    except Exception as e:
        print(f"   ❌ Error BD: {e}")
    
    print("\n🎯 Para ver la página funcionando:")
    print("   http://localhost:5000/dev/entrenar/test")

if __name__ == "__main__":
    test_simple()
