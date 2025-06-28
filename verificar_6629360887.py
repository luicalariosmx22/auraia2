#!/usr/bin/env python3
"""
🔍 Verificador directo para el usuario 6629360887
"""

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager

def verificar_usuario():
    """Verifica el usuario 6629360887"""
    telefono = "6629360887"
    
    print(f"🔍 VERIFICANDO USUARIO: {telefono}")
    print("=" * 50)
    
    # 1. Buscar en usuarios_clientes
    print("1️⃣ BÚSQUEDA EN usuarios_clientes:")
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("telefono", telefono) \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"   ✅ ENCONTRADO en usuarios_clientes")
            print(f"   📋 Nombre: {usuario.get('nombre')}")
            print(f"   📞 Teléfono: {usuario.get('telefono')}")
            print(f"   🏷️ Rol: {usuario.get('rol')}")
            print(f"   🔒 Activo: {usuario.get('activo')}")
            
            # Verificar privilegios
            usuario["tipo"] = "usuario_cliente"
            privilegios = PrivilegiosManager(usuario)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🎭 Tipo detectado: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            
            if not puede_tareas:
                print(f"   ❌ PROBLEMA: Usuario no puede leer tareas")
                # Mostrar privilegios completos
                resumen = privilegios.obtener_resumen_privilegios()
                print(f"   📊 Privilegios completos: {resumen}")
        else:
            print(f"   ❌ NO encontrado en usuarios_clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 2. Buscar en clientes
    print("\n2️⃣ BÚSQUEDA EN clientes:")
    try:
        response = supabase.table("clientes") \
            .select("*") \
            .eq("telefono", telefono) \
            .execute()
        
        if response.data:
            cliente = response.data[0]
            print(f"   ✅ ENCONTRADO en clientes")
            print(f"   📋 Nombre: {cliente.get('nombre_cliente')}")
            print(f"   📞 Teléfono: {cliente.get('telefono')}")
            
            # Verificar privilegios
            cliente["tipo"] = "cliente"
            privilegios = PrivilegiosManager(cliente)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🎭 Tipo detectado: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            
            # Verificar empresas
            if puede_tareas:
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
            print(f"   ❌ NO encontrado en clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")

if __name__ == "__main__":
    verificar_usuario()
