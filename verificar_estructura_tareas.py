#!/usr/bin/env python3
"""
🔍 Verificador de Estructura de Tabla Tareas
Muestra las columnas reales de la tabla tareas
"""

from clientes.aura.utils.supabase_client import supabase

def verificar_estructura_tareas():
    """Verifica la estructura real de la tabla tareas"""
    print("🔍 VERIFICANDO ESTRUCTURA DE TABLA 'tareas'")
    print("=" * 50)
    
    try:
        # Intentar obtener una tarea existente para ver las columnas
        response = supabase.table("tareas") \
            .select("*") \
            .limit(1) \
            .execute()
        
        if response.data:
            tarea = response.data[0]
            print("✅ Ejemplo de tarea existente:")
            print("📋 COLUMNAS DISPONIBLES:")
            for campo, valor in tarea.items():
                tipo_valor = type(valor).__name__
                print(f"   • {campo}: {valor} ({tipo_valor})")
        else:
            print("❌ No hay tareas existentes")
            
        # También intentar obtener el esquema
        print("\n📊 Intentando crear tarea de prueba para ver qué columnas acepta...")
        
    except Exception as e:
        print(f"💥 Error: {e}")

def crear_tarea_simple():
    """Crea una tarea con campos básicos"""
    print("\n📝 CREANDO TAREA SIMPLE")
    print("=" * 30)
    
    # Campos básicos que seguramente existen
    tarea_basica = {
        "titulo": "Tarea de Prueba",
        "descripcion": "Descripción de prueba",
    }
    
    try:
        response = supabase.table("tareas") \
            .insert(tarea_basica) \
            .execute()
        
        if response.data:
            print("✅ Tarea básica creada exitosamente")
            print(f"📋 Datos: {response.data[0]}")
        else:
            print("❌ Error al crear tarea básica")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        print("🔍 Esto nos ayuda a identificar qué campos son requeridos")

def buscar_empresas():
    """Busca empresas disponibles"""
    print("\n🏢 EMPRESAS DISPONIBLES:")
    try:
        response = supabase.table("cliente_empresas") \
            .select("*") \
            .execute()
        
        if response.data:
            for empresa in response.data:
                print(f"   • ID: {empresa.get('id')} - {empresa.get('nombre_empresa')}")
                print(f"     Campos: {list(empresa.keys())}")
        else:
            print("❌ No hay empresas")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    verificar_estructura_tareas()
    buscar_empresas()
    crear_tarea_simple()
