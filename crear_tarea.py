#!/usr/bin/env python3
"""
📝 Creador de Tareas
Script para agregar tareas fácilmente al sistema
"""

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

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

def listar_usuarios():
    """Lista todos los usuarios disponibles"""
    try:
        response = supabase.table("usuarios_clientes") \
            .select("id, nombre") \
            .eq("activo", True) \
            .execute()
        
        if response.data:
            print("👥 USUARIOS DISPONIBLES:")
            for i, usuario in enumerate(response.data, 1):
                print(f"   {i}. {usuario['nombre']} (ID: {usuario['id']})")
            return response.data
        else:
            print("❌ No hay usuarios registrados")
            return []
    except Exception as e:
        print(f"💥 Error: {e}")
        return []

def crear_tarea_interactiva():
    """Crea una tarea de forma interactiva"""
    print("📝 CREADOR DE TAREAS")
    print("=" * 40)
    
    # 1. Seleccionar empresa
    empresas = listar_empresas()
    if not empresas:
        return
    
    empresa_idx = int(input("\n🏢 Selecciona empresa (número): ")) - 1
    if empresa_idx < 0 or empresa_idx >= len(empresas):
        print("❌ Selección inválida")
        return
    
    empresa_id = empresas[empresa_idx]['id']
    empresa_nombre = empresas[empresa_idx]['nombre_empresa']
    
    # 2. Datos de la tarea
    titulo = input("📋 Título de la tarea: ")
    descripcion = input("📝 Descripción: ")
    
    # 3. Prioridad
    print("\n🎯 Prioridades:")
    print("   1. Baja")
    print("   2. Media") 
    print("   3. Alta")
    print("   4. Crítica")
    
    prioridad_map = {1: "baja", 2: "media", 3: "alta", 4: "critica"}
    prioridad_idx = int(input("Selecciona prioridad (1-4): "))
    prioridad = prioridad_map.get(prioridad_idx, "media")
    
    # 4. Fecha de vencimiento
    print("\n📅 Fecha de vencimiento:")
    print("   1. Hoy")
    print("   2. Mañana")
    print("   3. En 3 días")
    print("   4. En una semana")
    print("   5. Personalizada")
    
    fecha_idx = int(input("Selecciona opción (1-5): "))
    
    hoy = datetime.now()
    if fecha_idx == 1:
        fecha_vencimiento = hoy
    elif fecha_idx == 2:
        fecha_vencimiento = hoy + timedelta(days=1)
    elif fecha_idx == 3:
        fecha_vencimiento = hoy + timedelta(days=3)
    elif fecha_idx == 4:
        fecha_vencimiento = hoy + timedelta(days=7)
    else:
        dias = int(input("¿En cuántos días vence? "))
        fecha_vencimiento = hoy + timedelta(days=dias)
    
    # 5. Asignar usuario (opcional)
    usuarios = listar_usuarios()
    usuario_id = None
    
    if usuarios:
        asignar = input("\n👤 ¿Asignar a un usuario? (s/n): ").lower()
        if asignar == 's' or asignar == 'si':
            try:
                usuario_idx = int(input("Selecciona usuario (número): ")) - 1
                if 0 <= usuario_idx < len(usuarios):
                    usuario_id = usuarios[usuario_idx]['id']
                else:
                    print("⚠️ Selección inválida, no se asignará usuario")
            except ValueError:
                print("⚠️ Entrada inválida, no se asignará usuario")
    
    # 6. Crear la tarea
    nueva_tarea = {
        "titulo": titulo,
        "descripcion": descripcion,
        "empresa_id": empresa_id,
        "prioridad": prioridad,
        "fecha_vencimiento": fecha_vencimiento.isoformat(),
        "estatus": "pendiente"
    }
    
    # Agregar usuario si se asignó
    if usuario_id:
        nueva_tarea["usuario_empresa_id"] = usuario_id
    
    try:
        response = supabase.table("tareas") \
            .insert(nueva_tarea) \
            .execute()
        
        if response.data:
            print(f"\n✅ TAREA CREADA EXITOSAMENTE!")
            print(f"   📋 Título: {titulo}")
            print(f"   🏢 Empresa: {empresa_nombre}")
            print(f"   🎯 Prioridad: {prioridad}")
            print(f"   📅 Vence: {fecha_vencimiento.strftime('%d/%m/%Y')}")
            print(f"   🆔 ID: {response.data[0]['id']}")
        else:
            print("❌ Error al crear la tarea")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def crear_tarea_rapida(titulo, empresa_nombre, prioridad="media", dias_vencer=7):
    """Crea una tarea rápidamente"""
    try:
        # Buscar empresa
        empresa_response = supabase.table("cliente_empresas") \
            .select("id") \
            .ilike("nombre_empresa", f"%{empresa_nombre}%") \
            .limit(1) \
            .execute()
        
        if not empresa_response.data:
            print(f"❌ No se encontró empresa '{empresa_nombre}'")
            return
        
        empresa_id = empresa_response.data[0]['id']
        fecha_vencimiento = datetime.now() + timedelta(days=dias_vencer)
        
        nueva_tarea = {
            "titulo": titulo,
            "descripcion": f"Tarea creada automáticamente: {titulo}",
            "empresa_id": empresa_id,
            "prioridad": prioridad,
            "fecha_vencimiento": fecha_vencimiento.isoformat(),
            "estatus": "pendiente"
        }
        
        response = supabase.table("tareas") \
            .insert(nueva_tarea) \
            .execute()
        
        if response.data:
            print(f"✅ Tarea '{titulo}' creada para '{empresa_nombre}'")
            return response.data[0]['id']
        else:
            print("❌ Error al crear la tarea")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("📝 CREADOR DE TAREAS")
    print("=" * 30)
    print("1. Crear tarea interactiva")
    print("2. Crear tarea rápida")
    print("3. Listar empresas")
    print("4. Listar usuarios")
    
    opcion = input("\nSelecciona opción (1-4): ")
    
    if opcion == "1":
        crear_tarea_interactiva()
    elif opcion == "2":
        titulo = input("Título de la tarea: ")
        empresa = input("Nombre de la empresa: ")
        crear_tarea_rapida(titulo, empresa)
    elif opcion == "3":
        listar_empresas()
    elif opcion == "4":
        listar_usuarios()
    else:
        print("Opción inválida")
