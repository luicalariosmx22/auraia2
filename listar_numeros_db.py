#!/usr/bin/env python3
"""
🔍 Listador de todos los números en la base de datos
Para encontrar cómo está guardado 6629360887
"""

from clientes.aura.utils.supabase_client import supabase

def listar_todos_los_numeros():
    """Lista todos los números de teléfono en la base de datos"""
    telefono_objetivo = "6629360887"
    
    print(f"🔍 BUSCANDO NÚMERO: {telefono_objetivo}")
    print("=" * 60)
    
    # 1. Listar números en usuarios_clientes
    print("1️⃣ NÚMEROS EN usuarios_clientes:")
    try:
        response = supabase.table("usuarios_clientes") \
            .select("id, nombre, telefono, rol, activo, nombre_nora") \
            .execute()
        
        if response.data:
            print(f"   📊 Total registros: {len(response.data)}")
            for usuario in response.data:
                telefono_db = usuario.get('telefono', '')
                nombre = usuario.get('nombre', 'Sin nombre')
                rol = usuario.get('rol', 'Sin rol')
                activo = usuario.get('activo', False)
                nora = usuario.get('nombre_nora', '')
                
                # Verificar si contiene nuestro número
                contiene_numero = telefono_objetivo in telefono_db if telefono_db else False
                marcador = "🎯" if contiene_numero else "📱"
                
                print(f"   {marcador} {nombre} | {telefono_db} | {rol} | Activo:{activo} | Nora:{nora}")
                
                if contiene_numero:
                    print(f"      ✅ COINCIDENCIA ENCONTRADA!")
        else:
            print(f"   ❌ No hay datos en usuarios_clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 2. Listar números en clientes
    print("\n2️⃣ NÚMEROS EN clientes:")
    try:
        response = supabase.table("clientes") \
            .select("id, nombre_cliente, telefono, email, nombre_nora") \
            .execute()
        
        if response.data:
            print(f"   📊 Total registros: {len(response.data)}")
            for cliente in response.data:
                telefono_db = cliente.get('telefono', '')
                nombre = cliente.get('nombre_cliente', 'Sin nombre')
                email = cliente.get('email', 'Sin email')
                nora = cliente.get('nombre_nora', '')
                
                # Verificar si contiene nuestro número
                contiene_numero = telefono_objetivo in telefono_db if telefono_db else False
                marcador = "🎯" if contiene_numero else "📱"
                
                print(f"   {marcador} {nombre} | {telefono_db} | {email} | Nora:{nora}")
                
                if contiene_numero:
                    print(f"      ✅ COINCIDENCIA ENCONTRADA!")
        else:
            print(f"   ❌ No hay datos en clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 3. Buscar números que terminen en los últimos dígitos
    print(f"\n3️⃣ NÚMEROS QUE TERMINAN EN {telefono_objetivo[-6:]}:")
    try:
        # En usuarios_clientes
        response = supabase.table("usuarios_clientes") \
            .select("nombre, telefono") \
            .like("telefono", f"%{telefono_objetivo[-6:]}") \
            .execute()
        
        if response.data:
            print(f"   📊 usuarios_clientes - Coincidencias por últimos 6 dígitos:")
            for usuario in response.data:
                print(f"      🔍 {usuario.get('nombre')} | {usuario.get('telefono')}")
        
        # En clientes
        response2 = supabase.table("clientes") \
            .select("nombre_cliente, telefono") \
            .like("telefono", f"%{telefono_objetivo[-6:]}") \
            .execute()
        
        if response2.data:
            print(f"   📊 clientes - Coincidencias por últimos 6 dígitos:")
            for cliente in response2.data:
                print(f"      🔍 {cliente.get('nombre_cliente')} | {cliente.get('telefono')}")
                
    except Exception as e:
        print(f"   💥 Error: {e}")

if __name__ == "__main__":
    listar_todos_los_numeros()
