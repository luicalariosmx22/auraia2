#!/usr/bin/env python3
"""
🔍 Verificar datos existentes en la base de datos
"""

from supabase import create_client
from dotenv import load_dotenv
import os

def verificar_datos_bd():
    print("🔍 Verificando datos en la base de datos...")
    
    try:
        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Variables de entorno no configuradas")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Verificar todos los bloques
        print("\n📊 RESUMEN DE BASE DE DATOS:")
        print("=" * 40)
        
        # Total de registros
        res_total = supabase.table("conocimiento_nora").select("*").execute()
        print(f"📝 Total registros: {len(res_total.data)}")
        
        # Registros activos
        res_activos = supabase.table("conocimiento_nora").select("*").eq("activo", True).execute()
        print(f"✅ Registros activos: {len(res_activos.data)}")
        
        # Por nombre_nora
        nombres_nora = {}
        for registro in res_activos.data:
            nombre = registro.get('nombre_nora', 'sin_nombre')
            nombres_nora[nombre] = nombres_nora.get(nombre, 0) + 1
        
        print(f"\n🎯 DISTRIBUCIÓN POR NOMBRE_NORA:")
        for nombre, count in nombres_nora.items():
            print(f"   {nombre}: {count} bloques")
        
        # Mostrar algunos ejemplos
        if len(res_activos.data) > 0:
            print(f"\n📋 EJEMPLOS DE BLOQUES:")
            for i, bloque in enumerate(res_activos.data[:3]):
                print(f"\n{i+1}. ID: {bloque['id'][:8]}...")
                print(f"   Nora: {bloque.get('nombre_nora', 'N/A')}")
                print(f"   Contenido: {bloque.get('contenido', 'N/A')[:100]}...")
                print(f"   Etiquetas: {bloque.get('etiquetas', [])}")
                print(f"   Prioridad: {bloque.get('prioridad', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_endpoint_temporal():
    print("\n🧪 Probando endpoint temporal...")
    
    try:
        import requests
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get("http://localhost:5000/", timeout=2)
            print("✅ Servidor está corriendo")
        except:
            print("❌ Servidor no está corriendo - ejecuta: python run.py")
            return False
        
        # Probar endpoint temporal
        url = "http://localhost:5000/test/bloques/test"
        response = requests.get(url, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            if "bloques" in response.text.lower():
                # Contar cuántos bloques se muestran
                import re
                matches = re.findall(r'Total bloques:</strong> (\d+)', response.text)
                if matches:
                    total = matches[0]
                    print(f"✅ Endpoint temporal funciona - {total} bloques encontrados")
                else:
                    print("✅ Endpoint temporal funciona")
            else:
                print("⚠️ Endpoint responde pero sin datos")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE DATOS EXISTENTES")
    print("=" * 50)
    
    # 1. Verificar BD
    datos_ok = verificar_datos_bd()
    
    # 2. Test endpoint
    if datos_ok:
        test_endpoint_temporal()
    
    print("\n💡 CONCLUSIÓN:")
    if datos_ok:
        print("   ✅ Hay datos en la base de datos")
        print("   🔐 El problema es la autenticación en endpoints principales")
        print("   🎯 Solución: Usar endpoint /dev/entrenar/test para simular sesión")
    else:
        print("   ❌ No hay datos o hay problemas de conexión")
        print("   🎯 Solución: Crear datos de prueba primero")
