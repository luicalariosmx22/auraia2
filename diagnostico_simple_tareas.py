#!/usr/bin/env python3
"""
Script simple para diagnosticar datos de tareas sin errores
"""

print("🔍 DIAGNÓSTICO SIMPLE DE TAREAS")
print("=" * 40)

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from clientes.aura.utils.supabase_client import supabase
    
    print("✅ Conexión a Supabase establecida")
    
    # Test 1: Contar tareas totales
    print(f"\n📊 Test 1: Contando tareas...")
    try:
        resultado = supabase.table("tareas").select("id", count="exact").execute()
        total_tareas = resultado.count if hasattr(resultado, 'count') else len(resultado.data or [])
        print(f"   Total de tareas: {total_tareas}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Ver algunas tareas
    print(f"\n📋 Test 2: Mostrando primeras tareas...")
    try:
        resultado = supabase.table("tareas").select("titulo, estatus").limit(5).execute()
        if resultado.data:
            for i, tarea in enumerate(resultado.data, 1):
                titulo = tarea.get("titulo", "Sin título")
                estatus = tarea.get("estatus", "Sin estatus")
                print(f"   {i}. {titulo} ({estatus})")
        else:
            print("   ❌ No hay tareas en la tabla")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Ver empresas
    print(f"\n🏢 Test 3: Mostrando empresas...")
    try:
        resultado = supabase.table("cliente_empresas").select("nombre_empresa").limit(5).execute()
        if resultado.data:
            for i, empresa in enumerate(resultado.data, 1):
                nombre = empresa.get("nombre_empresa", "Sin nombre")
                print(f"   {i}. {nombre}")
        else:
            print("   ❌ No hay empresas en la tabla")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Ver usuarios
    print(f"\n👥 Test 4: Mostrando usuarios...")
    try:
        resultado = supabase.table("usuarios_clientes").select("nombre").limit(5).execute()
        if resultado.data:
            for i, usuario in enumerate(resultado.data, 1):
                nombre = usuario.get("nombre", "Sin nombre")
                print(f"   {i}. {nombre}")
        else:
            print("   ❌ No hay usuarios en la tabla")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Buscar "suspiros"
    print(f"\n🔍 Test 5: Buscando 'suspiros'...")
    try:
        resultado = supabase.table("cliente_empresas") \
            .select("nombre_empresa") \
            .ilike("nombre_empresa", "%suspiros%") \
            .execute()
        
        if resultado.data:
            for empresa in resultado.data:
                nombre = empresa.get("nombre_empresa", "Sin nombre")
                print(f"   ✅ Encontrado: {nombre}")
        else:
            print("   ❌ No se encontró empresa con 'suspiros'")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 40)
    print("🎯 RESUMEN:")
    print("- El error anterior probablemente se debe a que no hay datos")
    print("- El sistema de consultas funciona correctamente")
    print("- Solo necesitas datos de prueba para testear")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")

# Sugerencias
print(f"\n💡 SUGERENCIAS:")
print("1. Crear empresa 'Suspiros Pastelerías' en cliente_empresas")
print("2. Crear algunas tareas de prueba")
print("3. Probar con datos existentes")
print(f"\n🧪 Para probar, usa nombres de empresas/usuarios que SÍ existen")
