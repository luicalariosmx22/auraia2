#!/usr/bin/env python3
"""
📝 Creador de Tareas CORREGIDO v2
Versión que maneja correctamente las restricciones de la BD
"""

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta
import uuid

def listar_usuarios_empresa(empresa_id):
    """Lista usuarios disponibles para una empresa específica"""
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
            print("❌ No hay usuarios activos")
            return []
    except Exception as e:
        print(f"💥 Error: {e}")
        return []

def crear_tarea_completa():
    """Crea una tarea con todos los campos requeridos"""
    print("📝 CREADOR DE TAREAS COMPLETO")
    print("=" * 40)
    
    # 1. Buscar empresa
    nombre_empresa = input("🏢 Nombre de la empresa: ")
    
    try:
        empresa_response = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .ilike("nombre_empresa", f"%{nombre_empresa}%") \
            .limit(1) \
            .execute()
        
        if not empresa_response.data:
            print(f"❌ No se encontró empresa '{nombre_empresa}'")
            return
        
        empresa_id = empresa_response.data[0]['id']
        empresa_nombre_real = empresa_response.data[0]['nombre_empresa']
        print(f"✅ Empresa encontrada: {empresa_nombre_real}")
        
    except Exception as e:
        print(f"💥 Error buscando empresa: {e}")
        return
    
    # 2. Seleccionar usuario (obligatorio)
    usuarios = listar_usuarios_empresa(empresa_id)
    if not usuarios:
        print("❌ No se pueden crear tareas sin usuarios disponibles")
        return
    
    try:
        usuario_idx = int(input("👤 Selecciona usuario (número): ")) - 1
        if usuario_idx < 0 or usuario_idx >= len(usuarios):
            print("❌ Selección inválida")
            return
        
        usuario_id = usuarios[usuario_idx]['id']
        usuario_nombre = usuarios[usuario_idx]['nombre']
        print(f"✅ Usuario asignado: {usuario_nombre}")
        
    except ValueError:
        print("❌ Entrada inválida")
        return
    
    # 3. Datos de la tarea
    titulo = input("📋 Título de la tarea: ")
    descripcion = input("📝 Descripción: ") or f"Tarea: {titulo}"
    
    # 4. Prioridad
    prioridad = input("🎯 Prioridad (baja/media/alta/critica): ").lower()
    if prioridad not in ["baja", "media", "alta", "critica"]:
        prioridad = "media"
    
    # 5. Fecha límite
    try:
        dias = int(input("📅 Días para vencer (default 7): ") or "7")
        fecha_limite = (datetime.now() + timedelta(days=dias)).date().isoformat()
    except ValueError:
        fecha_limite = (datetime.now() + timedelta(days=7)).date().isoformat()
    
    # 6. Crear tarea con estructura correcta
    nueva_tarea = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": f"TASK-{uuid.uuid4().hex[:6].upper()}",
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "estatus": "pendiente",
        "fecha_limite": fecha_limite,
        "empresa_id": empresa_id,
        "usuario_empresa_id": usuario_id,  # Campo obligatorio
        "nombre_nora": "aura",
        "activo": True,
        "asignada_a_empresa": True
    }
    
    print(f"\n🔄 Creando tarea...")
    print(f"   📋 {titulo}")
    print(f"   🏢 {empresa_nombre_real}")
    print(f"   👤 {usuario_nombre}")
    print(f"   🎯 Prioridad: {prioridad}")
    print(f"   📅 Fecha límite: {fecha_limite}")
    
    try:
        response = supabase.table("tareas") \
            .insert(nueva_tarea) \
            .execute()
        
        if response.data:
            tarea_creada = response.data[0]
            print(f"\n✅ TAREA CREADA EXITOSAMENTE!")
            print(f"   🆔 ID: {tarea_creada['id']}")
            print(f"   📋 Código: {tarea_creada['codigo_tarea']}")
            print(f"   📝 Título: {tarea_creada['titulo']}")
            print(f"   🏢 Empresa: {empresa_nombre_real}")
            print(f"   👤 Asignado a: {usuario_nombre}")
        else:
            print("❌ Error: No se recibieron datos de la tarea creada")
            
    except Exception as e:
        print(f"💥 Error al crear tarea: {e}")

def crear_tareas_ejemplo():
    """Crea varias tareas de ejemplo"""
    print("🎯 CREANDO TAREAS DE EJEMPLO...")
    
    # Buscar primera empresa disponible
    try:
        empresas = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .limit(1) \
            .execute()
        
        if not empresas.data:
            print("❌ No hay empresas disponibles")
            return
        
        empresa_id = empresas.data[0]['id']
        empresa_nombre = empresas.data[0]['nombre_empresa']
        
        # Buscar primer usuario disponible
        usuarios = supabase.table("usuarios_clientes") \
            .select("id, nombre") \
            .eq("activo", True) \
            .limit(1) \
            .execute()
        
        if not usuarios.data:
            print("❌ No hay usuarios disponibles")
            return
        
        usuario_id = usuarios.data[0]['id']
        usuario_nombre = usuarios.data[0]['nombre']
        
        # Crear 3 tareas de ejemplo
        tareas_ejemplo = [
            {
                "titulo": "Revisar presupuesto Q2",
                "descripcion": "Análisis del presupuesto del segundo trimestre",
                "prioridad": "alta"
            },
            {
                "titulo": "Actualizar redes sociales",
                "descripcion": "Publicar contenido semanal en todas las plataformas",
                "prioridad": "media"
            },
            {
                "titulo": "Reunión con equipo",
                "descripcion": "Revisión de objetivos mensuales",
                "prioridad": "baja"
            }
        ]
        
        for i, tarea_data in enumerate(tareas_ejemplo, 1):
            nueva_tarea = {
                "id": str(uuid.uuid4()),
                "codigo_tarea": f"TASK-EJ{i:03d}",
                "titulo": tarea_data["titulo"],
                "descripcion": tarea_data["descripcion"],
                "prioridad": tarea_data["prioridad"],
                "estatus": "pendiente",
                "fecha_limite": (datetime.now() + timedelta(days=i*3)).date().isoformat(),
                "empresa_id": empresa_id,
                "usuario_empresa_id": usuario_id,
                "nombre_nora": "aura",
                "activo": True,
                "asignada_a_empresa": True
            }
            
            try:
                response = supabase.table("tareas") \
                    .insert(nueva_tarea) \
                    .execute()
                
                if response.data:
                    print(f"   ✅ Tarea {i}: {tarea_data['titulo']}")
                else:
                    print(f"   ❌ Error en tarea {i}")
                    
            except Exception as e:
                print(f"   💥 Error en tarea {i}: {e}")
        
        print(f"\n🎉 Tareas de ejemplo creadas para:")
        print(f"   🏢 Empresa: {empresa_nombre}")
        print(f"   👤 Usuario: {usuario_nombre}")
        
    except Exception as e:
        print(f"💥 Error general: {e}")

if __name__ == "__main__":
    print("📝 CREADOR DE TAREAS CORREGIDO")
    print("=" * 35)
    print("1. Crear tarea completa")
    print("2. Crear tareas de ejemplo")
    print("3. Listar empresas")
    
    opcion = input("\nSelecciona opción (1-3): ")
    
    if opcion == "1":
        crear_tarea_completa()
    elif opcion == "2":
        crear_tareas_ejemplo()
    elif opcion == "3":
        try:
            empresas = supabase.table("cliente_empresas") \
                .select("id, nombre_empresa") \
                .execute()
            
            if empresas.data:
                print("🏢 EMPRESAS DISPONIBLES:")
                for empresa in empresas.data:
                    print(f"   • {empresa['nombre_empresa']} (ID: {empresa['id']})")
            else:
                print("❌ No hay empresas registradas")
        except Exception as e:
            print(f"💥 Error: {e}")
    else:
        print("Opción inválida")
