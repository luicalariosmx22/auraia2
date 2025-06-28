#!/usr/bin/env python3
"""
👤 Agregar Usuario 6629360887
Script para agregar el usuario específico como empleado
"""

from clientes.aura.utils.supabase_client import supabase

def agregar_usuario_empleado():
    """Agrega el usuario 6629360887 como empleado"""
    
    nuevo_usuario = {
        "nombre": "Usuario WhatsApp",
        "telefono": "6629360887",
        "correo": "usuario@auramarketing.com",
        "rol": "empleado",
        "nombre_nora": "aura",
        "activo": True,
        "es_supervisor": False,
        "es_supervisor_tareas": False,
        "modulos": ["tareas", "base_conocimiento"]
    }
    
    print("👤 AGREGANDO USUARIO 6629360887")
    print("=" * 40)
    print(f"📝 Datos: {nuevo_usuario}")
    
    try:
        # Verificar si ya existe
        response_check = supabase.table("usuarios_clientes") \
            .select("id") \
            .eq("telefono", "6629360887") \
            .execute()
        
        if response_check.data:
            print("⚠️ El usuario ya existe")
            return
        
        # Crear usuario
        response = supabase.table("usuarios_clientes") \
            .insert(nuevo_usuario) \
            .execute()
        
        if response.data:
            print("✅ USUARIO CREADO EXITOSAMENTE!")
            print(f"   🆔 ID: {response.data[0]['id']}")
            print(f"   👤 Nombre: {response.data[0]['nombre']}")
            print(f"   📞 Teléfono: {response.data[0]['telefono']}")
            print(f"   🏷️ Rol: {response.data[0]['rol']}")
        else:
            print("❌ Error al crear usuario")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    agregar_usuario_empleado()
