#!/usr/bin/env python3
"""
🔍 Verificador de estructura de tabla tareas
"""

from clientes.aura.utils.supabase_client import supabase

def verificar_estructura_tareas():
    """Verifica la estructura de la tabla tareas"""
    try:
        # Obtener una tarea existente para ver las columnas
        response = supabase.table("tareas") \
            .select("*") \
            .limit(1) \
            .execute()
        
        if response.data:
            print("📊 COLUMNAS DISPONIBLES EN TABLA 'tareas':")
            for columna in response.data[0].keys():
                print(f"   • {columna}")
        else:
            print("❌ No hay datos en la tabla tareas")
            # Intentar crear una tarea simple para ver qué columnas acepta
            print("🧪 Intentando insertar tarea de prueba...")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    verificar_estructura_tareas()
