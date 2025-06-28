#!/usr/bin/env python3
"""
🔍 Verificador con búsqueda por últimos 10 dígitos
Busca 6629360887 usando LIKE %6629360887
"""

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager

def verificar_usuario_ultimos_digitos():
    """Verifica el usuario buscando por últimos 10 dígitos"""
    telefono = "6629360887"
    ultimos_10 = telefono[-10:] if len(telefono) >= 10 else telefono
    
    print(f"🔍 VERIFICANDO USUARIO: {telefono}")
    print(f"📱 Buscando por últimos 10 dígitos: {ultimos_10}")
    print("=" * 60)
    
    # 1. Buscar en usuarios_clientes con LIKE
    print("1️⃣ BÚSQUEDA EN usuarios_clientes (LIKE):")
    try:
        # Búsqueda con LIKE por últimos dígitos
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .like("telefono", f"%{ultimos_10}") \
            .execute()
        
        if response.data:
            print(f"   ✅ ENCONTRADO {len(response.data)} registro(s) en usuarios_clientes")
            for i, usuario in enumerate(response.data, 1):
                print(f"\n   📋 USUARIO {i}:")
                print(f"      ID: {usuario.get('id')}")
                print(f"      Nombre: {usuario.get('nombre')}")
                print(f"      Teléfono: {usuario.get('telefono')}")
                print(f"      Rol: {usuario.get('rol')}")
                print(f"      Activo: {usuario.get('activo')}")
                print(f"      Nora: {usuario.get('nombre_nora')}")
                
                # Verificar privilegios
                usuario["tipo"] = "usuario_cliente"
                privilegios = PrivilegiosManager(usuario)
                tipo = privilegios.get_tipo_usuario()
                puede_tareas = privilegios.puede_acceder("tareas", "read")
                
                print(f"      🎭 Tipo detectado: {tipo}")
                print(f"      📝 Puede leer tareas: {puede_tareas}")
                
                if not puede_tareas:
                    print(f"      ❌ PROBLEMA: Usuario no puede leer tareas")
                    # Mostrar por qué no puede
                    resumen = privilegios.obtener_resumen_privilegios()
                    print(f"      📊 Privilegios: {resumen}")
        else:
            print(f"   ❌ NO encontrado en usuarios_clientes con LIKE")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 2. Buscar en clientes con LIKE
    print("\n2️⃣ BÚSQUEDA EN clientes (LIKE):")
    try:
        # Búsqueda con LIKE por últimos dígitos
        response = supabase.table("clientes") \
            .select("*") \
            .like("telefono", f"%{ultimos_10}") \
            .execute()
        
        if response.data:
            print(f"   ✅ ENCONTRADO {len(response.data)} registro(s) en clientes")
            for i, cliente in enumerate(response.data, 1):
                print(f"\n   📋 CLIENTE {i}:")
                print(f"      ID: {cliente.get('id')}")
                print(f"      Nombre: {cliente.get('nombre_cliente')}")
                print(f"      Teléfono: {cliente.get('telefono')}")
                print(f"      Email: {cliente.get('email')}")
                print(f"      Nora: {cliente.get('nombre_nora')}")
                
                # Verificar privilegios
                cliente["tipo"] = "cliente"
                privilegios = PrivilegiosManager(cliente)
                tipo = privilegios.get_tipo_usuario()
                puede_tareas = privilegios.puede_acceder("tareas", "read")
                
                print(f"      🎭 Tipo detectado: {tipo}")
                print(f"      📝 Puede leer tareas: {puede_tareas}")
                
                # Verificar empresas si es cliente
                if puede_tareas:
                    cliente_id = cliente.get("id")
                    empresas = supabase.table("cliente_empresas") \
                        .select("*") \
                        .eq("cliente_id", cliente_id) \
                        .execute()
                    
                    if empresas.data:
                        print(f"      🏢 Empresas: {len(empresas.data)}")
                        for emp in empresas.data:
                            print(f"         • {emp.get('nombre_empresa', 'Sin nombre')}")
                    else:
                        print(f"      ❌ SIN empresas asignadas")
                        print(f"         📌 ESTO PUEDE SER EL PROBLEMA - Cliente sin empresas")
        else:
            print(f"   ❌ NO encontrado en clientes con LIKE")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 3. Buscar variaciones comunes del número
    print("\n3️⃣ BÚSQUEDA DE VARIACIONES:")
    variaciones = [
        f"52{telefono}",      # +52
        f"+52{telefono}",     # +52 con +
        f"1{telefono}",       # código de área
        f"whatsapp:{telefono}",
        f"whatsapp:+52{telefono}",
        f"+521{telefono}",    # celular México
    ]
    
    for variacion in variaciones:
        print(f"   🔍 Probando: {variacion}")
        try:
            # Buscar en usuarios_clientes
            response = supabase.table("usuarios_clientes") \
                .select("id, nombre, telefono, rol") \
                .eq("telefono", variacion) \
                .execute()
            
            if response.data:
                print(f"      ✅ ENCONTRADO en usuarios_clientes: {response.data[0].get('nombre')}")
                
            # Buscar en clientes
            response2 = supabase.table("clientes") \
                .select("id, nombre_cliente, telefono") \
                .eq("telefono", variacion) \
                .execute()
            
            if response2.data:
                print(f"      ✅ ENCONTRADO en clientes: {response2.data[0].get('nombre_cliente')}")
                
        except Exception as e:
            print(f"      💥 Error con {variacion}: {e}")

if __name__ == "__main__":
    verificar_usuario_ultimos_digitos()
