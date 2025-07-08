#!/usr/bin/env python3
"""
📝 Creador Simple de Tareas
Versión mínima para crear tareas rápidamente
"""

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

def crear_tarea_simple():
    """Crea una tarea con datos mínimos"""
    
    # Datos básicos de la tarea
    nueva_tarea = {
        "titulo": "Tarea de Prueba",
        "descripcion": "Esta es una tarea de prueba del sistema",
        "empresa_id": 1,  # Usar ID de empresa existente
        "prioridad": "media",
        "fecha_vencimiento": (datetime.now() + timedelta(days=7)).isoformat(),
        "estatus": "pendiente"
    }
    
    try:
        print("📝 Creando tarea de prueba...")
        print(f"   Datos: {nueva_tarea}")
        
        response = supabase.table("tareas") \
            .insert(nueva_tarea) \
            .execute()
        
        if response.data:
            print("✅ TAREA CREADA EXITOSAMENTE!")
            print(f"   ID: {response.data[0].get('id')}")
            print(f"   Título: {response.data[0].get('titulo')}")
        else:
            print("❌ No se pudo crear la tarea")
            print(f"   Response: {response}")
            
    except Exception as e:
        print(f"💥 Error detallado: {e}")
        print(f"   Tipo: {type(e)}")

def listar_empresas_simple():
    """Lista empresas disponibles"""
    try:
        response = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .limit(5) \
            .execute()
        
        if response.data:
            print("🏢 EMPRESAS DISPONIBLES:")
            for empresa in response.data:
                print(f"   ID {empresa['id']}: {empresa['nombre_empresa']}")
        else:
            print("❌ No hay empresas")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("📝 CREADOR SIMPLE DE TAREAS")
    print("=" * 30)
    
    print("\n1. Listando empresas...")
    listar_empresas_simple()
    
    print("\n2. Creando tarea de prueba...")
    crear_tarea_simple()
