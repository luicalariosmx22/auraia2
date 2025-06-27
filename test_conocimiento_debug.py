#!/usr/bin/env python3
"""
Script para debug de la funcionalidad de conocimiento
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

def test_conexion_supabase():
    """Probar conexión a Supabase"""
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Variables de entorno no configuradas")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente de Supabase creado")
        
        # Probar consulta a conocimiento_nora
        res = supabase.table("conocimiento_nora").select("count", count="exact").execute()
        print(f"✅ Conexión exitosa - Total registros: {res.count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_esquema_tabla():
    """Verificar esquema de la tabla conocimiento_nora"""
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener una muestra de datos para ver la estructura
        res = supabase.table("conocimiento_nora").select("*").limit(1).execute()
        
        if res.data:
            print("✅ Estructura de tabla conocimiento_nora:")
            for key, value in res.data[0].items():
                print(f"   - {key}: {type(value).__name__} = {value}")
        else:
            print("⚠️ No hay datos en la tabla conocimiento_nora")
            print("📋 Intentando insertar datos de prueba...")
            
            # Crear datos de prueba
            test_data = {
                "nombre_nora": "test_nora",
                "contenido": "Esta es información de prueba para testing",
                "etiquetas": ["test", "prueba", "debug"],
                "origen": "manual",
                "prioridad": False,
                "activo": True
            }
            
            res_insert = supabase.table("conocimiento_nora").insert(test_data).execute()
            if res_insert.data:
                print(f"✅ Datos de prueba insertados: {res_insert.data[0]['id']}")
            else:
                print("❌ Error al insertar datos de prueba")
        
    except Exception as e:
        print(f"❌ Error verificando esquema: {e}")

def test_consulta_por_nora(nombre_nora="test_nora"):
    """Probar consulta específica por nombre de Nora"""
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
        
        print(f"🔍 Consulta para '{nombre_nora}':")
        print(f"   Total encontrados: {len(res.data)}")
        
        for bloque in res.data:
            print(f"   - ID: {bloque['id'][:8]}...")
            print(f"     Contenido: {bloque['contenido'][:50]}...")
            print(f"     Etiquetas: {bloque['etiquetas']}")
            print(f"     Prioridad: {bloque['prioridad']}")
            
    except Exception as e:
        print(f"❌ Error en consulta: {e}")

if __name__ == "__main__":
    print("🧪 === TEST DE CONOCIMIENTO DE NORA ===")
    
    print("\n1️⃣ Probando conexión a Supabase...")
    if test_conexion_supabase():
        print("\n2️⃣ Verificando esquema de tabla...")
        test_esquema_tabla()
        
        print("\n3️⃣ Probando consulta específica...")
        test_consulta_por_nora("test_nora")
        
        # También probar con un nombre real si está disponible
        if len(sys.argv) > 1:
            nombre_real = sys.argv[1]
            print(f"\n4️⃣ Probando con nombre real '{nombre_real}'...")
            test_consulta_por_nora(nombre_real)
    
    print("\n✅ Test completado.")
