#!/usr/bin/env python3
"""
📝 Creador de Tareas CORREGIDO
Script para agregar tareas con la estructura correcta
"""

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta
import uuid
import random
import string

def crear_tarea_simple(titulo, empresa_nombre, descripcion="", prioridad="media", dias_vencer=7):
    """Crea una tarea con la estructura correcta"""
    try:
        # Buscar empresa
        empresa_response = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .ilike("nombre_empresa", f"%{empresa_nombre}%") \
            .limit(1) \
            .execute()
        
        if not empresa_response.data:
            print(f"❌ No se encontró empresa '{empresa_nombre}'")
            return
        
        empresa_id = empresa_response.data[0]['id']
        empresa_real = empresa_response.data[0]['nombre_empresa']
        fecha_limite = datetime.now() + timedelta(days=dias_vencer)
        
        # Generar código único para la tarea
        codigo_tarea = f"TASK-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        nueva_tarea = {
            "id": str(uuid.uuid4()),
            "codigo_tarea": codigo_tarea,
            "titulo": titulo,
            "descripcion": descripcion or f"Tarea: {titulo}",
            "prioridad": prioridad,
            "estatus": "pendiente",
            "fecha_limite": fecha_limite.strftime("%Y-%m-%d"),
            "empresa_id": empresa_id,
            "nombre_nora": "aura",
            "activo": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "asignada_a_empresa": True
        }
        
        print(f"🔄 Creando tarea con datos: {nueva_tarea}")
        
        response = supabase.table("tareas") \
            .insert(nueva_tarea) \
            .execute()
        
        if response.data:
            print(f"✅ TAREA CREADA EXITOSAMENTE!")
            print(f"   📋 Título: {titulo}")
            print(f"   🏢 Empresa: {empresa_real}")
            print(f"   🎯 Prioridad: {prioridad}")
            print(f"   📅 Vence: {fecha_limite.strftime('%d/%m/%Y')}")
            print(f"   🆔 ID: {response.data[0]['id']}")
            print(f"   📋 Código: {codigo_tarea}")
            return response.data[0]['id']
        else:
            print(f"❌ Error al crear la tarea: {response}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def listar_empresas():
    """Lista todas las empresas disponibles"""
    try:
        response = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .execute()
        
        if response.data:
            print("🏢 EMPRESAS DISPONIBLES:")
            for i, empresa in enumerate(response.data, 1):
                print(f"   {i}. {empresa['nombre_empresa']} (ID: {empresa['id']})")
            return response.data
        else:
            print("❌ No hay empresas registradas")
            return []
    except Exception as e:
        print(f"💥 Error: {e}")
        return []

def crear_tareas_ejemplo():
    """Crea algunas tareas de ejemplo"""
    print("📝 CREANDO TAREAS DE EJEMPLO")
    print("=" * 40)
    
    tareas_ejemplo = [
        ("Revisar presupuesto mensual", "Aura Marketing", "Revisar y analizar el presupuesto del mes", "alta", 3),
        ("Contactar proveedor", "Aura Marketing", "Llamar al proveedor principal para coordinar entrega", "media", 5),
        ("Actualizar redes sociales", "Aura Marketing", "Publicar contenido en redes sociales", "baja", 7),
        ("Preparar presentación cliente", "Aura Marketing", "Crear presentación para reunión con cliente", "alta", 2),
    ]
    
    for titulo, empresa, descripcion, prioridad, dias in tareas_ejemplo:
        print(f"\n🔄 Creando: {titulo}")
        crear_tarea_simple(titulo, empresa, descripcion, prioridad, dias)

if __name__ == "__main__":
    print("📝 CREADOR DE TAREAS CORREGIDO")
    print("=" * 40)
    print("1. Crear tarea personalizada")
    print("2. Crear tareas de ejemplo")
    print("3. Listar empresas")
    
    opcion = input("\nSelecciona opción (1-3): ")
    
    if opcion == "1":
        titulo = input("📋 Título de la tarea: ")
        empresa = input("🏢 Nombre de la empresa: ")
        descripcion = input("📝 Descripción (opcional): ")
        prioridad = input("🎯 Prioridad (baja/media/alta/critica): ") or "media"
        dias = int(input("📅 Días para vencer (default 7): ") or "7")
        
        crear_tarea_simple(titulo, empresa, descripcion, prioridad, dias)
        
    elif opcion == "2":
        crear_tareas_ejemplo()
        
    elif opcion == "3":
        listar_empresas()
        
    else:
        print("Opción inválida")
