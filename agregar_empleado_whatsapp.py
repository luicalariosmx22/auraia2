#!/usr/bin/env python3
"""
👨‍💼 Agregador de Usuario Empleado
Script para agregar el usuario 6629360887 como empleado
"""

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime

def agregar_usuario_empleado():
    """Agrega el usuario 6629360887 como empleado"""
    
    telefono = "6629360887"
    
    # Datos del nuevo empleado
    nuevo_empleado = {
        "nombre": "Usuario Test WhatsApp",
        "telefono": telefono,
        "correo": "test@auramarketing.com",
        "rol": "admin",  # Darle rol de admin para que pueda ver todas las tareas
        "nombre_nora": "aura",
        "activo": True,
        "es_supervisor": True,  # Para que tenga permisos de supervisor
        "modulos": ["tareas", "base_conocimiento", "reportes"]
    }
    
    try:
        print(f"👨‍💼 AGREGANDO USUARIO EMPLEADO: {telefono}")
        print("=" * 50)
        print(f"📋 Datos: {nuevo_empleado}")
        
        # Verificar si ya existe
        response_check = supabase.table("usuarios_clientes") \
            .select("id, nombre") \
            .eq("telefono", telefono) \
            .execute()
        
        if response_check.data:
            print(f"⚠️ Usuario ya existe: {response_check.data[0]['nombre']}")
            return response_check.data[0]
        
        # Insertar nuevo usuario
        response = supabase.table("usuarios_clientes") \
            .insert(nuevo_empleado) \
            .execute()
        
        if response.data:
            usuario_creado = response.data[0]
            print(f"✅ USUARIO EMPLEADO CREADO!")
            print(f"   🆔 ID: {usuario_creado['id']}")
            print(f"   👤 Nombre: {usuario_creado['nombre']}")
            print(f"   📞 Teléfono: {usuario_creado['telefono']}")
            print(f"   🏷️ Rol: {usuario_creado['rol']}")
            print(f"   🔒 Supervisor: {usuario_creado['es_supervisor']}")
            
            return usuario_creado
        else:
            print("❌ Error: No se pudo crear el usuario")
            return None
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

def verificar_usuario_creado(telefono):
    """Verifica que el usuario fue creado correctamente"""
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("telefono", telefono) \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"\n🔍 VERIFICACIÓN USUARIO {telefono}:")
            print(f"   ✅ Existe en base de datos")
            print(f"   👤 Nombre: {usuario['nombre']}")
            print(f"   🏷️ Rol: {usuario['rol']}")
            print(f"   🔒 Activo: {usuario['activo']}")
            print(f"   🎯 Nombre Nora: {usuario['nombre_nora']}")
            
            # Verificar privilegios
            from clientes.aura.auth.privilegios import PrivilegiosManager
            
            usuario_datos = {
                "tipo": "usuario_cliente",
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "rol": usuario["rol"],
                "es_supervisor": usuario["es_supervisor"]
            }
            
            privilegios = PrivilegiosManager(usuario_datos)
            puede_tareas = privilegios.puede_acceder("tareas", "read")
            
            print(f"   📝 Puede leer tareas: {puede_tareas}")
            print(f"   🎭 Tipo detectado: {privilegios.get_tipo_usuario()}")
            
            return True
        else:
            print(f"❌ Usuario {telefono} no encontrado")
            return False
            
    except Exception as e:
        print(f"💥 Error verificando: {e}")
        return False

if __name__ == "__main__":
    print("👨‍💼 AGREGADOR DE USUARIO EMPLEADO")
    print("=" * 40)
    
    # Agregar usuario
    usuario = agregar_usuario_empleado()
    
    if usuario:
        # Verificar que se creó correctamente
        verificar_usuario_creado("6629360887")
        
        print(f"\n🎉 ¡LISTO! El usuario 6629360887 ya puede:")
        print(f"   📱 Escribir a Nora por WhatsApp")
        print(f"   📋 Consultar \"mis tareas\"")
        print(f"   🏢 Ver tareas de su empresa")
        print(f"   ✨ Recibir mensaje de bienvenida personalizado")
    else:
        print(f"\n❌ No se pudo crear el usuario")
