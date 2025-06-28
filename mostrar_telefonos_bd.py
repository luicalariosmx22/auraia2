#!/usr/bin/env python3
"""
🔍 Ver todos los números de teléfono en la base de datos
Para comparar con 6629360887
"""

from clientes.aura.utils.supabase_client import supabase

def mostrar_todos_los_telefonos():
    """Muestra todos los números de teléfono guardados"""
    
    print("📱 NÚMEROS EN LA BASE DE DATOS")
    print("=" * 60)
    
    # 1. Mostrar usuarios_clientes
    print("1️⃣ USUARIOS_CLIENTES:")
    try:
        response = supabase.table("usuarios_clientes") \
            .select("id, nombre, telefono, correo, rol, activo") \
            .execute()
        
        if response.data:
            print(f"   📊 Total registros: {len(response.data)}")
            for usuario in response.data:
                telefono = usuario.get('telefono', 'Sin teléfono')
                nombre = usuario.get('nombre', 'Sin nombre')
                activo = usuario.get('activo', False)
                estado = "✅" if activo else "❌"
                print(f"   {estado} {telefono} - {nombre}")
        else:
            print("   ❌ No hay usuarios en usuarios_clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 2. Mostrar clientes
    print("\n2️⃣ CLIENTES:")
    try:
        response = supabase.table("clientes") \
            .select("id, nombre_cliente, telefono, email") \
            .execute()
        
        if response.data:
            print(f"   📊 Total registros: {len(response.data)}")
            for cliente in response.data:
                telefono = cliente.get('telefono', 'Sin teléfono')
                nombre = cliente.get('nombre_cliente', 'Sin nombre')
                print(f"   📞 {telefono} - {nombre}")
        else:
            print("   ❌ No hay clientes registrados")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 3. Buscar números que contengan 6629360887
    print("\n3️⃣ BÚSQUEDA ESPECÍFICA DE '6629360887':")
    
    # En usuarios_clientes
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .like("telefono", "%6629360887%") \
            .execute()
        
        if response.data:
            print("   ✅ ENCONTRADO en usuarios_clientes:")
            for usuario in response.data:
                print(f"      📞 {usuario.get('telefono')} - {usuario.get('nombre')}")
        else:
            print("   ❌ No encontrado en usuarios_clientes")
    except Exception as e:
        print(f"   💥 Error usuarios_clientes: {e}")
    
    # En clientes
    try:
        response = supabase.table("clientes") \
            .select("*") \
            .like("telefono", "%6629360887%") \
            .execute()
        
        if response.data:
            print("   ✅ ENCONTRADO en clientes:")
            for cliente in response.data:
                print(f"      📞 {cliente.get('telefono')} - {cliente.get('nombre_cliente')}")
        else:
            print("   ❌ No encontrado en clientes")
    except Exception as e:
        print(f"   💥 Error clientes: {e}")
    
    # 4. Buscar números similares (últimos 8 dígitos)
    print("\n4️⃣ BÚSQUEDA POR ÚLTIMOS 8 DÍGITOS (29360887):")
    
    # En usuarios_clientes
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .like("telefono", "%29360887") \
            .execute()
        
        if response.data:
            print("   ✅ ENCONTRADO en usuarios_clientes (últimos 8):")
            for usuario in response.data:
                print(f"      📞 {usuario.get('telefono')} - {usuario.get('nombre')}")
        else:
            print("   ❌ No encontrado en usuarios_clientes (últimos 8)")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # En clientes
    try:
        response = supabase.table("clientes") \
            .select("*") \
            .like("telefono", "%29360887") \
            .execute()
        
        if response.data:
            print("   ✅ ENCONTRADO en clientes (últimos 8):")
            for cliente in response.data:
                print(f"      📞 {cliente.get('telefono')} - {cliente.get('nombre_cliente')}")
        else:
            print("   ❌ No encontrado en clientes (últimos 8)")
    except Exception as e:
        print(f"   💥 Error: {e}")

if __name__ == "__main__":
    mostrar_todos_los_telefonos()
