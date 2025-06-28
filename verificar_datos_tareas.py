#!/usr/bin/env python3
"""
Script para verificar qué empresas y usuarios tienen tareas registradas
Así puedes probar el sistema con datos reales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verificar_datos_tareas():
    """Verifica qué empresas y usuarios tienen tareas registradas"""
    print("🔍 VERIFICANDO DATOS DE TAREAS EN LA BASE DE DATOS")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # 1. Verificar empresas con tareas
        print("\n🏢 EMPRESAS CON TAREAS:")
        print("-" * 30)
        
        empresas_con_tareas = supabase.table("tareas") \
            .select("""
                empresa_id,
                cliente_empresas!tareas_empresa_id_fkey(nombre_empresa),
                COUNT(*) as total_tareas
            """) \
            .not_.is_("empresa_id", "null") \
            .eq("activo", True) \
            .execute()
        
        if empresas_con_tareas.data:
            for empresa in empresas_con_tareas.data[:10]:  # Limitar a 10
                nombre_empresa = empresa.get("cliente_empresas", {}).get("nombre_empresa", "Sin nombre")
                print(f"   📊 {nombre_empresa}")
        else:
            print("   ❌ No hay empresas con tareas registradas")
        
        # 2. Verificar usuarios con tareas
        print(f"\n👥 USUARIOS CON TAREAS:")
        print("-" * 30)
        
        usuarios_con_tareas = supabase.table("tareas") \
            .select("""
                usuario_empresa_id,
                usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre),
                COUNT(*) as total_tareas
            """) \
            .not_.is_("usuario_empresa_id", "null") \
            .eq("activo", True) \
            .execute()
        
        if usuarios_con_tareas.data:
            for usuario in usuarios_con_tareas.data[:10]:  # Limitar a 10
                nombre_usuario = usuario.get("usuarios_clientes", {}).get("nombre", "Sin nombre")
                print(f"   📊 {nombre_usuario}")
        else:
            print("   ❌ No hay usuarios con tareas registradas")
        
        # 3. Verificar empresas disponibles (sin tareas necesariamente)
        print(f"\n🏢 TODAS LAS EMPRESAS DISPONIBLES:")
        print("-" * 30)
        
        todas_empresas = supabase.table("cliente_empresas") \
            .select("nombre_empresa") \
            .limit(10) \
            .execute()
        
        if todas_empresas.data:
            for empresa in todas_empresas.data:
                print(f"   📋 {empresa['nombre_empresa']}")
        else:
            print("   ❌ No hay empresas registradas")
        
        # 4. Verificar usuarios disponibles
        print(f"\n👥 TODOS LOS USUARIOS DISPONIBLES:")
        print("-" * 30)
        
        todos_usuarios = supabase.table("usuarios_clientes") \
            .select("nombre") \
            .eq("activo", True) \
            .limit(10) \
            .execute()
        
        if todos_usuarios.data:
            for usuario in todos_usuarios.data:
                print(f"   📋 {usuario['nombre']}")
        else:
            print("   ❌ No hay usuarios registrados")
        
        # 5. Sugerencias de prueba
        print(f"\n💡 SUGERENCIAS PARA PRUEBAS:")
        print("-" * 30)
        
        if empresas_con_tareas.data:
            primera_empresa = empresas_con_tareas.data[0].get("cliente_empresas", {}).get("nombre_empresa")
            if primera_empresa:
                print(f"   🧪 Prueba: 'tareas de {primera_empresa}'")
        
        if usuarios_con_tareas.data:
            primer_usuario = usuarios_con_tareas.data[0].get("usuarios_clientes", {}).get("nombre")
            if primer_usuario:
                print(f"   🧪 Prueba: '¿Qué tareas tiene {primer_usuario}?'")
        
        if todas_empresas.data and not empresas_con_tareas.data:
            print(f"   💡 Hay empresas pero sin tareas - considera crear tareas de prueba")
        
        if todos_usuarios.data and not usuarios_con_tareas.data:
            print(f"   💡 Hay usuarios pero sin tareas - considera crear tareas de prueba")
            
        print(f"\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        print(f"Verifica la conexión a Supabase")

def crear_tarea_prueba():
    """Crea una tarea de prueba para Suspiros Pastelerías"""
    print(f"\n🛠️ CREAR TAREA DE PRUEBA PARA SUSPIROS PASTELERÍAS")
    print("-" * 50)
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Buscar si existe la empresa
        empresa = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .ilike("nombre_empresa", "%suspiros%") \
            .execute()
        
        if empresa.data:
            print(f"✅ Empresa encontrada: {empresa.data[0]['nombre_empresa']}")
            
            # Buscar un usuario para asignar la tarea
            usuario = supabase.table("usuarios_clientes") \
                .select("id, nombre") \
                .eq("activo", True) \
                .limit(1) \
                .execute()
            
            if usuario.data:
                print(f"✅ Usuario encontrado: {usuario.data[0]['nombre']}")
                
                # Crear tarea de prueba
                nueva_tarea = {
                    "codigo_tarea": "TEST-001",
                    "titulo": "Tarea de prueba para consultas",
                    "descripcion": "Esta es una tarea de prueba para verificar el sistema de consultas",
                    "estatus": "pendiente",
                    "prioridad": "media",
                    "empresa_id": empresa.data[0]["id"],
                    "usuario_empresa_id": usuario.data[0]["id"],
                    "nombre_nora": "aura",
                    "activo": True
                }
                
                resultado = supabase.table("tareas").insert(nueva_tarea).execute()
                
                if resultado.data:
                    print(f"✅ Tarea creada exitosamente")
                    print(f"📝 Ahora puedes probar: 'tareas de suspiros pastelerías'")
                else:
                    print(f"❌ Error creando tarea")
            else:
                print(f"❌ No se encontró usuario para asignar")
        else:
            print(f"❌ No se encontró empresa 'Suspiros Pastelerías'")
            print(f"💡 Primero necesitas crear la empresa en cliente_empresas")
            
    except Exception as e:
        print(f"❌ Error creando tarea de prueba: {e}")

if __name__ == "__main__":
    verificar_datos_tareas()
    
    respuesta = input(f"\n¿Crear una tarea de prueba para Suspiros Pastelerías? (s/n): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        crear_tarea_prueba()
