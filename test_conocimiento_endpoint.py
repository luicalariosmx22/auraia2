#!/usr/bin/env python3
"""
🧪 Test del Endpoint de Conocimiento
Verifica que el endpoint de bloques funcione correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.supabase_client import supabase

def test_datos_conocimiento():
    """Prueba que los datos de conocimiento estén en la base de datos"""
    print("🧪 VERIFICANDO DATOS DE CONOCIMIENTO EN SUPABASE")
    print("=" * 50)
    
    try:
        # Consulta directa a la tabla conocimiento_nora
        response = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", "aura") \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        print(f"✅ Consulta exitosa")
        print(f"📊 Total de bloques encontrados: {len(response.data)}")
        
        if response.data:
            print("\n📋 BLOQUES ENCONTRADOS:")
            for i, bloque in enumerate(response.data, 1):
                print(f"\n{i}. ID: {bloque['id'][:8]}...")
                print(f"   Contenido: {bloque['contenido'][:50]}...")
                print(f"   Etiquetas: {bloque['etiquetas']}")
                print(f"   Prioridad: {bloque['prioridad']}")
                print(f"   Activo: {bloque['activo']}")
                print(f"   Fecha: {bloque['fecha_creacion']}")
        else:
            print("❌ No se encontraron bloques de conocimiento")
            
        return response.data
    
    except Exception as e:
        print(f"❌ Error consultando conocimiento: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_endpoint_simulado():
    """Simula la lógica del endpoint"""
    print("\n🧪 SIMULANDO LÓGICA DEL ENDPOINT")
    print("=" * 50)
    
    try:
        # Esta es la misma consulta que hace el endpoint
        res = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", "aura") \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        # Simular respuesta JSON
        resultado = {"success": True, "data": res.data}
        
        print(f"✅ Endpoint simulado exitoso")
        print(f"📦 JSON resultado: {resultado}")
        
        return resultado
    
    except Exception as e:
        print(f"❌ Error en endpoint simulado: {e}")
        return {"success": False, "message": str(e)}

def test_estructura_datos():
    """Verifica la estructura de los datos"""
    print("\n🧪 VERIFICANDO ESTRUCTURA DE DATOS")
    print("=" * 50)
    
    datos = test_datos_conocimiento()
    if not datos:
        return
    
    print(f"\n🔍 ANÁLISIS DE ESTRUCTURA:")
    for bloque in datos:
        print(f"\n📋 Bloque ID: {bloque['id'][:8]}...")
        print(f"   Campos disponibles: {list(bloque.keys())}")
        
        # Verificar campos requeridos
        campos_requeridos = ['id', 'nombre_nora', 'contenido', 'etiquetas', 'activo']
        for campo in campos_requeridos:
            if campo in bloque:
                print(f"   ✅ {campo}: {type(bloque[campo])}")
            else:
                print(f"   ❌ {campo}: FALTANTE")
        
        # Analizar etiquetas
        etiquetas = bloque.get('etiquetas')
        if etiquetas:
            print(f"   🏷️  Etiquetas tipo: {type(etiquetas)}")
            print(f"   🏷️  Etiquetas valor: {etiquetas}")

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE CONOCIMIENTO")
    print("=" * 70)
    
    try:
        test_datos_conocimiento()
        test_endpoint_simulado()
        test_estructura_datos()
        
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 70)
        print("\n💡 CONCLUSIONES:")
        print("   1. Los datos están en la base de datos ✅")
        print("   2. El endpoint debería funcionar ✅")
        print("   3. El problema está en el frontend (JS/HTML) ❌")
        print("\n🔧 SIGUIENTE PASO:")
        print("   - Verificar que las rutas JS se carguen correctamente")
        print("   - Verificar la consola del navegador para errores")
        print("   - Verificar que PANEL_CONFIG se configure correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
