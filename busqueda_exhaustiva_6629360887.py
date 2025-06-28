#!/usr/bin/env python3
"""
🔍 Búsqueda exhaustiva del usuario 6629360887
"""

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager

def busqueda_exhaustiva():
    """Búsqueda exhaustiva del usuario"""
    
    numero = "6629360887"
    print(f"🔍 BÚSQUEDA EXHAUSTIVA: {numero}")
    print("=" * 50)
    
    # Lista de campos donde puede estar el teléfono
    campos_telefono = ["telefono", "whatsapp", "celular", "phone"]
    
    # 1. Buscar en usuarios_clientes
    print("1️⃣ USUARIOS_CLIENTES:")
    
    for campo in campos_telefono:
        try:
            # Búsqueda exacta
            response = supabase.table("usuarios_clientes") \
                .select("*") \
                .eq(campo, numero) \
                .execute()
            
            if response.data:
                print(f"   ✅ ENCONTRADO en campo '{campo}' (exacto)")
                usuario = response.data[0]
                print(f"      📋 Nombre: {usuario.get('nombre')}")
                print(f"      📞 Teléfono: {usuario.get(campo)}")
                print(f"      🏷️ Rol: {usuario.get('rol')}")
                
                # Verificar privilegios
                usuario["tipo"] = "usuario_cliente"
                privilegios = PrivilegiosManager(usuario)
                puede_tareas = privilegios.puede_acceder("tareas", "read")
                print(f"      📝 Puede leer tareas: {puede_tareas}")
                return usuario
                
            # Búsqueda con LIKE
            response = supabase.table("usuarios_clientes") \
                .select("*") \
                .like(campo, f"%{numero}%") \
                .execute()
            
            if response.data:
                print(f"   ✅ ENCONTRADO en campo '{campo}' (LIKE)")
                for usuario in response.data:
                    print(f"      📋 {usuario.get('nombre')} - {usuario.get(campo)}")
                return response.data[0]
                
        except Exception as e:
            # Campo no existe, continuar
            continue
    
    print("   ❌ No encontrado en usuarios_clientes")
    
    # 2. Buscar en clientes
    print("\n2️⃣ CLIENTES:")
    
    for campo in campos_telefono:
        try:
            # Búsqueda exacta
            response = supabase.table("clientes") \
                .select("*") \
                .eq(campo, numero) \
                .execute()
            
            if response.data:
                print(f"   ✅ ENCONTRADO en campo '{campo}' (exacto)")
                cliente = response.data[0]
                print(f"      📋 Nombre: {cliente.get('nombre_cliente')}")
                print(f"      📞 Teléfono: {cliente.get(campo)}")
                
                # Verificar privilegios
                cliente["tipo"] = "cliente"
                privilegios = PrivilegiosManager(cliente)
                puede_tareas = privilegios.puede_acceder("tareas", "read")
                print(f"      📝 Puede leer tareas: {puede_tareas}")
                
                if puede_tareas:
                    # Verificar empresas
                    empresas = supabase.table("cliente_empresas") \
                        .select("*") \
                        .eq("cliente_id", cliente.get("id")) \
                        .execute()
                    
                    if empresas.data:
                        print(f"      🏢 Empresas: {len(empresas.data)}")
                    else:
                        print(f"      ❌ Sin empresas asignadas")
                
                return cliente
                
            # Búsqueda con LIKE
            response = supabase.table("clientes") \
                .select("*") \
                .like(campo, f"%{numero}%") \
                .execute()
            
            if response.data:
                print(f"   ✅ ENCONTRADO en campo '{campo}' (LIKE)")
                for cliente in response.data:
                    print(f"      📋 {cliente.get('nombre_cliente')} - {cliente.get(campo)}")
                return response.data[0]
                
        except Exception as e:
            # Campo no existe, continuar
            continue
    
    print("   ❌ No encontrado en clientes")
    
    # 3. Mostrar algunos registros de muestra
    print("\n3️⃣ MUESTRA DE REGISTROS EXISTENTES:")
    
    try:
        usuarios = supabase.table("usuarios_clientes") \
            .select("nombre, telefono") \
            .limit(5) \
            .execute()
        
        print("   👥 Usuarios muestra:")
        for u in usuarios.data:
            print(f"      📞 {u.get('telefono')} - {u.get('nombre')}")
    except:
        pass
    
    try:
        clientes = supabase.table("clientes") \
            .select("nombre_cliente, telefono") \
            .limit(5) \
            .execute()
        
        print("   🏢 Clientes muestra:")
        for c in clientes.data:
            print(f"      📞 {c.get('telefono')} - {c.get('nombre_cliente')}")
    except:
        pass
    
    return None

if __name__ == "__main__":
    usuario_encontrado = busqueda_exhaustiva()
    
    if not usuario_encontrado:
        print("\n🚨 CONCLUSIÓN:")
        print("   ❌ El usuario 6629360887 NO está registrado en la base de datos")
        print("   📝 Debe ser agregado a 'usuarios_clientes' o 'clientes'")
        print("   🔧 O verificar que el número esté en otro formato")
