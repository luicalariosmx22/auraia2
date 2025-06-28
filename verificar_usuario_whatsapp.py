#!/usr/bin/env python3
"""
🔍 Verificador de Usuario WhatsApp
Diagnóstica el usuario 6629360887 y sus permisos
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.auth.privilegios import PrivilegiosManager
from clientes.aura.utils.consultor_tareas import ConsultorTareas

def verificar_usuario_whatsapp():
    """Verifica el usuario de WhatsApp y sus permisos"""
    telefono = "6629360887"
    
    print(f"🔍 VERIFICANDO USUARIO WHATSAPP: {telefono}")
    print("=" * 50)
    
    try:
        # Conectar a la base de datos
        supabase = SupabaseClient()
        
        # 1. Buscar en tabla clientes
        print("\n1️⃣ BUSCANDO EN TABLA CLIENTES:")
        cliente = supabase.buscar_cliente_por_telefono(telefono)
        if cliente:
            print(f"✅ Cliente encontrado:")
            print(f"   ID: {cliente.get('id')}")
            print(f"   Nombre: {cliente.get('nombre', 'N/A')}")
            print(f"   Tipo: {cliente.get('tipo', 'N/A')}")
            print(f"   Rol: {cliente.get('rol', 'N/A')}")
            print(f"   Es Supervisor: {cliente.get('es_supervisor', False)}")
            print(f"   Datos completos: {cliente}")
        else:
            print("❌ No encontrado en tabla clientes")
        
        # 2. Buscar en tabla usuarios_clientes
        print("\n2️⃣ BUSCANDO EN TABLA USUARIOS_CLIENTES:")
        try:
            resultado = supabase.client.table("usuarios_clientes").select("*").eq("telefono", telefono).execute()
            if resultado.data:
                usuario = resultado.data[0]
                print(f"✅ Usuario encontrado:")
                print(f"   ID: {usuario.get('id')}")
                print(f"   Nombre: {usuario.get('nombre', 'N/A')}")
                print(f"   Tipo: {usuario.get('tipo', 'N/A')}")
                print(f"   Rol: {usuario.get('rol', 'N/A')}")
                print(f"   Datos completos: {usuario}")
            else:
                print("❌ No encontrado en tabla usuarios_clientes")
        except Exception as e:
            print(f"❌ Error consultando usuarios_clientes: {e}")
        
        # 3. Verificar privilegios
        print("\n3️⃣ VERIFICANDO PRIVILEGIOS:")
        if cliente:
            manager = PrivilegiosManager(cliente)
            tipo_usuario = manager.get_tipo_usuario()
            print(f"   Tipo determinado: {tipo_usuario}")
            
            # Verificar acceso a tareas
            puede_leer_tareas = manager.puede_acceder("tareas", "read")
            print(f"   Puede leer tareas: {puede_leer_tareas}")
            
            # Mostrar todas las tablas accesibles
            tablas_accesibles = manager.obtener_tablas_accesibles("read")
            print(f"   Tablas con acceso de lectura: {tablas_accesibles}")
        
        # 4. Verificar empresas del cliente
        print("\n4️⃣ VERIFICANDO EMPRESAS DEL CLIENTE:")
        if cliente:
            try:
                consultor = ConsultorTareas(supabase)
                empresas = consultor.obtener_empresas_cliente(cliente.get('id'))
                if empresas:
                    print(f"✅ Cliente tiene acceso a {len(empresas)} empresa(s):")
                    for empresa in empresas:
                        print(f"   - {empresa.get('nombre')} (ID: {empresa.get('id')})")
                else:
                    print("❌ Cliente no tiene empresas asignadas")
            except Exception as e:
                print(f"❌ Error consultando empresas: {e}")
        
        # 5. Probar consulta de tareas
        print("\n5️⃣ PROBANDO CONSULTA DE TAREAS:")
        if cliente:
            try:
                consultor = ConsultorTareas(supabase)
                mensaje = "mis tareas"
                es_consulta_cliente = consultor.es_consulta_cliente(mensaje)
                print(f"   '¿{mensaje}' es consulta de cliente?: {es_consulta_cliente}")
                
                if es_consulta_cliente:
                    respuesta = consultor.procesar_consulta_cliente(cliente, mensaje)
                    print(f"   Respuesta: {respuesta[:200]}...")
                else:
                    print("   No se procesó como consulta de cliente")
                    
            except Exception as e:
                print(f"❌ Error en consulta de tareas: {e}")
        
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_usuario_whatsapp()
