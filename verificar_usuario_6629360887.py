#!/usr/bin/env python3
"""
🔍 Verificador específico para el usuario 6629360887
Analiza por qué no tiene permisos para consultar tareas
"""

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager
from clientes.aura.handlers.process_message import identificar_usuario_por_telefono

def verificar_usuario_completo():
    """
    Verifica completamente el usuario 6629360887
    """
    telefono = "6629360887"
    
    print(f"🔍 VERIFICANDO USUARIO: {telefono}")
    print("=" * 50)
    
    # 1. Buscar en usuarios_clientes
    print("1️⃣ BÚSQUEDA EN usuarios_clientes:")
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .or_(f"telefono.eq.{telefono},whatsapp.eq.{telefono}") \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"   ✅ ENCONTRADO en usuarios_clientes")
            print(f"   📋 Datos: {usuario}")
            
            # Verificar privilegios
            privilegios = PrivilegiosManager(usuario)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🔒 Tipo de usuario: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            
        else:
            print(f"   ❌ NO encontrado en usuarios_clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 2. Buscar en clientes
    print("\n2️⃣ BÚSQUEDA EN clientes:")
    try:
        response = supabase.table("clientes") \
            .select("*") \
            .or_(f"telefono.eq.{telefono},whatsapp.eq.{telefono}") \
            .execute()
        
        if response.data:
            cliente = response.data[0]
            print(f"   ✅ ENCONTRADO en clientes")
            print(f"   📋 Datos: {cliente}")
            
            # Verificar privilegios
            privilegios = PrivilegiosManager(cliente)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🔒 Tipo de usuario: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            
        else:
            print(f"   ❌ NO encontrado en clientes")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 3. Usar función de identificación
    print("\n3️⃣ USANDO FUNCIÓN DE IDENTIFICACIÓN:")
    try:
        usuario_identificado = identificar_usuario_por_telefono(telefono)
        
        if usuario_identificado:
            print(f"   ✅ IDENTIFICADO")
            print(f"   📋 Datos: {usuario_identificado}")
            
            # Verificar privilegios
            privilegios = PrivilegiosManager(usuario_identificado)
            tipo = privilegios.get_tipo_usuario()
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   🔒 Tipo de usuario: {tipo}")
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            
        else:
            print(f"   ❌ NO identificado por la función")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # 4. Verificar empresas del cliente
    if usuario_identificado and usuario_identificado.get("tipo") == "cliente":
        print("\n4️⃣ VERIFICANDO EMPRESAS DEL CLIENTE:")
        try:
            cliente_id = usuario_identificado.get("id")
            
            empresas = supabase.table("cliente_empresas") \
                .select("*") \
                .eq("cliente_id", cliente_id) \
                .execute()
            
            if empresas.data:
                print(f"   ✅ Cliente tiene {len(empresas.data)} empresas:")
                for emp in empresas.data:
                    print(f"      📊 {emp.get('nombre_empresa', 'Sin nombre')}")
            else:
                print(f"   ❌ Cliente SIN empresas asignadas")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

if __name__ == "__main__":
    verificar_usuario_completo()
