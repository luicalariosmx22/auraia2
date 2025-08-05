"""
Script para probar el sistema de notificaciones
Inserta una configuración de prueba y envía una notificación de test
"""

import os
import sys
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.notificaciones import enviar_notificaciones_alerta, obtener_configuracion_notificaciones

def configurar_usuario_prueba():
    """Inserta configuración de notificaciones para prueba"""
    try:
        # Configuración de ejemplo - cambia estos valores
        config_prueba = {
            'nombre_nora': 'aura_demo',  # Cambia por tu nombre_nora
            'email_notificaciones': True,
            'sms_notificaciones': False,  # Cambiar a True si quieres probar SMS también
            'email': 'tu_email@ejemplo.com',  # CAMBIA POR TU EMAIL REAL
            'telefono': '+521234567890',  # Tu número si vas a probar SMS
            'solo_alta_prioridad': False  # False para recibir todas las alertas
        }
        
        print("📝 Insertando configuración de prueba...")
        
        # Insertar o actualizar configuración
        response = supabase.table("configuracion_notificaciones") \
            .upsert(config_prueba) \
            .execute()
        
        print(f"✅ Configuración insertada: {response.data}")
        return True
        
    except Exception as e:
        print(f"❌ Error al insertar configuración: {e}")
        return False

def crear_alerta_prueba():
    """Crea una alerta de prueba"""
    try:
        alerta_prueba = {
            'nombre': 'Prueba de Notificaciones',
            'descripcion': 'Esta es una alerta de prueba para verificar que las notificaciones funcionan correctamente.',
            'tipo': 'sistema',
            'prioridad': 'alta',
            'nombre_nora': 'aura_demo',  # Cambia por tu nombre_nora
            'activa': True,
            'vista': False,
            'resuelta': False,
            'datos': {
                'empresa_nombre': 'Empresa de Prueba',
                'test': True
            }
        }
        
        print("🚨 Creando alerta de prueba...")
        
        response = supabase.table("alertas") \
            .insert(alerta_prueba) \
            .execute()
        
        if response.data:
            alerta_id = response.data[0]['id']
            print(f"✅ Alerta de prueba creada con ID: {alerta_id}")
            return alerta_id, alerta_prueba
        else:
            print("❌ No se pudo crear la alerta")
            return None, None
            
    except Exception as e:
        print(f"❌ Error al crear alerta de prueba: {e}")
        return None, None

def probar_notificaciones():
    """Prueba completa del sistema de notificaciones"""
    print("🧪 INICIANDO PRUEBA DEL SISTEMA DE NOTIFICACIONES")
    print("=" * 50)
    
    # Paso 1: Configurar usuario
    print("\n📋 PASO 1: Configuración de usuario")
    if not configurar_usuario_prueba():
        print("❌ Falló la configuración de usuario")
        return
    
    # Paso 2: Crear alerta de prueba
    print("\n🚨 PASO 2: Crear alerta de prueba")
    alerta_id, alerta_data = crear_alerta_prueba()
    if not alerta_id:
        print("❌ Falló la creación de alerta")
        return
    
    # Paso 3: Obtener configuración
    print("\n⚙️ PASO 3: Obtener configuración de notificaciones")
    config = obtener_configuracion_notificaciones('aura_demo')
    print(f"📧 Email habilitado: {config.get('email_notificaciones')}")
    print(f"📱 SMS habilitado: {config.get('sms_notificaciones')}")
    print(f"📬 Email destino: {config.get('email')}")
    
    # Paso 4: Enviar notificaciones
    print("\n📤 PASO 4: Enviar notificaciones")
    notificaciones_enviadas = enviar_notificaciones_alerta(alerta_data, config)
    
    if notificaciones_enviadas:
        print(f"✅ Notificaciones enviadas exitosamente: {notificaciones_enviadas}")
        print("\n🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
        print("💡 Revisa tu email para ver la notificación")
    else:
        print("❌ No se enviaron notificaciones")
        print("🔍 Verifica tu configuración en .env.local")
    
    # Paso 5: Limpiar (opcional)
    print(f"\n🧹 LIMPIEZA: ¿Eliminar alerta de prueba {alerta_id}? (s/n)")
    respuesta = input().lower()
    if respuesta == 's':
        try:
            supabase.table("alertas").delete().eq("id", alerta_id).execute()
            print("✅ Alerta de prueba eliminada")
        except Exception as e:
            print(f"❌ Error al eliminar alerta: {e}")

if __name__ == "__main__":
    print("🚀 ANTES DE EJECUTAR:")
    print("1. Cambia 'nombre_nora' por tu valor real")
    print("2. Cambia 'tu_email@ejemplo.com' por tu email real")
    print("3. Verifica que tu .env.local tenga las variables de email")
    print("\n¿Continuar? (s/n)")
    
    respuesta = input().lower()
    if respuesta == 's':
        probar_notificaciones()
    else:
        print("👋 Prueba cancelada. Actualiza la configuración y vuelve a ejecutar.")
