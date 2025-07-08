#!/usr/bin/env python3
"""
Script simple para verificar datos en la tabla de tareas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verificar_datos_tareas():
    """Verificar qué datos hay en las tablas relacionadas con tareas"""
    print("🔍 VERIFICACIÓN DE DATOS EN TABLAS DE TAREAS")
    print("=" * 50)
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # 1. Verificar empresas
        print("\n📊 EMPRESAS REGISTRADAS:")
        print("-" * 30)
        
        empresas = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .limit(10) \
            .execute()
        
        if empresas.data:
            for i, empresa in enumerate(empresas.data, 1):
                print(f"{i}. {empresa.get('nombre_empresa', 'Sin nombre')} (ID: {empresa.get('id')})")
        else:
            print("No hay empresas registradas")
        
        # 2. Verificar usuarios
        print(f"\n👥 USUARIOS REGISTRADOS:")
        print("-" * 30)
        
        usuarios = supabase.table("usuarios_clientes") \
            .select("id, nombre, nombre_nora") \
            .eq("nombre_nora", "aura") \
            .limit(10) \
            .execute()
        
        if usuarios.data:
            for i, usuario in enumerate(usuarios.data, 1):
                print(f"{i}. {usuario.get('nombre', 'Sin nombre')} (ID: {usuario.get('id')})")
        else:
            print("No hay usuarios registrados para Nora 'aura'")
        
        # 3. Verificar tareas existentes
        print(f"\n📋 TAREAS EXISTENTES:")
        print("-" * 30)
        
        tareas = supabase.table("tareas") \
            .select("""
                titulo, 
                descripcion, 
                estatus,
                usuarios_clientes!tareas_usuario_empresa_id_fkey(nombre),
                cliente_empresas!tareas_empresa_id_fkey(nombre_empresa)
            """) \
            .eq("nombre_nora", "aura") \
            .eq("activo", True) \
            .limit(10) \
            .execute()
        
        if tareas.data:
            for i, tarea in enumerate(tareas.data, 1):
                usuario_nombre = "Sin asignar"
                empresa_nombre = "Sin empresa"
                
                if tarea.get('usuarios_clientes'):
                    usuario_nombre = tarea['usuarios_clientes'].get('nombre', 'Sin nombre')
                
                if tarea.get('cliente_empresas'):
                    empresa_nombre = tarea['cliente_empresas'].get('nombre_empresa', 'Sin nombre')
                
                print(f"{i}. {tarea.get('titulo', 'Sin título')}")
                print(f"   Usuario: {usuario_nombre}")
                print(f"   Empresa: {empresa_nombre}")
                print(f"   Estatus: {tarea.get('estatus', 'Sin estatus')}")
                print()
        else:
            print("No hay tareas registradas para Nora 'aura'")
        
        # 4. Sugerencias de prueba
        print(f"\n💡 SUGERENCIAS PARA PROBAR:")
        print("-" * 30)
        
        if empresas.data:
            empresa_ejemplo = empresas.data[0].get('nombre_empresa')
            print(f"✅ Probar: 'tareas de la empresa {empresa_ejemplo}'")
        
        if usuarios.data:
            usuario_ejemplo = usuarios.data[0].get('nombre')
            print(f"✅ Probar: 'tareas de {usuario_ejemplo}'")
        
        if not tareas.data:
            print("⚠️ No hay tareas registradas.")
            print("💡 Necesitas crear tareas primero para poder consultarlas.")
            print("📝 Como SuperAdmin, puedes crear tareas desde el panel.")
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        print("Verificar conexión a Supabase")

if __name__ == "__main__":
    verificar_datos_tareas()
