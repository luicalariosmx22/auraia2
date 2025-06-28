#!/usr/bin/env python3
"""
🔍 Verificador simple para el usuario 6629360887
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager

def verificar_usuario_simple():
    """
    Verificación simple del usuario 6629360887
    """
    telefono = "6629360887"
    
    print(f"🔍 VERIFICANDO USUARIO: {telefono}")
    print("=" * 50)
    
    # 1. Buscar en usuarios_clientes
    print("1️⃣ BÚSQUEDA EN usuarios_clientes:")
    try:
        # Búsqueda directa
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("telefono", telefono) \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"   ✅ ENCONTRADO (búsqueda directa)")
            print(f"   📋 ID: {usuario.get('id')}")
            print(f"   👤 Nombre: {usuario.get('nombre')}")
            print(f"   📞 Teléfono: {usuario.get('telefono')}")
            print(f"   🏷️ Rol: {usuario.get('rol')}")
            print(f"   🔒 Activo: {usuario.get('activo')}")
            
            # Agregar tipo para verificar privilegios
            usuario["tipo"] = "usuario_cliente"
            
            # Verificar privilegios
            privilegios = PrivilegiosManager(usuario)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🎭 Tipo detectado: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
        else:
            print(f"   ❌ NO encontrado (búsqueda directa)")
            
        # Búsqueda con LIKE por últimos dígitos
        response2 = supabase.table("usuarios_clientes") \
            .select("*") \
            .like("telefono", f"%{telefono}") \
            .execute()
            
        if response2.data:
            print(f"   ✅ ENCONTRADO (búsqueda con LIKE)")
            for user in response2.data:
                print(f"      📋 {user.get('nombre')} - {user.get('telefono')}")
        else:
            print(f"   ❌ NO encontrado (búsqueda con LIKE)")
            
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 2. Buscar en clientes
    print("\n2️⃣ BÚSQUEDA EN clientes:")
    try:
        # Búsqueda directa
        response = supabase.table("clientes") \
            .select("*") \
            .eq("telefono", telefono) \
            .execute()
        
        if response.data:
            cliente = response.data[0]
            print(f"   ✅ ENCONTRADO (búsqueda directa)")
            print(f"   📋 ID: {cliente.get('id')}")
            print(f"   👤 Nombre: {cliente.get('nombre_cliente')}")
            print(f"   📞 Teléfono: {cliente.get('telefono')}")
            
            # Agregar tipo para verificar privilegios
            cliente["tipo"] = "cliente"
            
            # Verificar privilegios
            privilegios = PrivilegiosManager(cliente)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🎭 Tipo detectado: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            
            # Verificar empresas
            cliente_id = cliente.get("id")
            empresas = supabase.table("cliente_empresas") \
                .select("*") \
                .eq("cliente_id", cliente_id) \
                .execute()
            
            if empresas.data:
                print(f"   🏢 Empresas: {len(empresas.data)}")
                for emp in empresas.data:
                    print(f"      • {emp.get('nombre_empresa', 'Sin nombre')}")
            else:
                print(f"   ❌ SIN empresas asignadas")
        else:
            print(f"   ❌ NO encontrado (búsqueda directa)")
            
        # Búsqueda con LIKE
        response2 = supabase.table("clientes") \
            .select("*") \
            .like("telefono", f"%{telefono}") \
            .execute()
            
        if response2.data:
            print(f"   ✅ ENCONTRADO (búsqueda con LIKE)")
            for cliente in response2.data:
                print(f"      📋 {cliente.get('nombre_cliente')} - {cliente.get('telefono')}")
        else:
            print(f"   ❌ NO encontrado (búsqueda con LIKE)")
            
    except Exception as e:
        print(f"   💥 Error: {e}")

if __name__ == "__main__":
    verificar_usuario_simple()
