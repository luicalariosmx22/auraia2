#!/usr/bin/env python3
"""
🚀 SCRIPT DE PRUEBA: Registro Masivo de Webhooks Meta Ads
Verifica que el botón de registro masivo funcione correctamente
"""

import sys
import os
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.meta_webhook_helpers import registrar_webhooks_en_cuentas_activas
import requests

def verificar_configuracion():
    """Verifica que todo esté configurado para webhook masivo"""
    print("🔍 VERIFICANDO CONFIGURACIÓN WEBHOOK MASIVO")
    print("=" * 60)
    
    # 1. Variables de entorno
    vars_requeridas = [
        'META_ACCESS_TOKEN',
        'META_WEBHOOK_SECRET', 
        'META_WEBHOOK_VERIFY_TOKEN',
        'META_APP_ID',
        'BASE_URL'
    ]
    
    print("\n1️⃣ Variables de entorno:")
    todas_configuradas = True
    for var in vars_requeridas:
        valor = os.getenv(var)
        if valor:
            print(f"   ✅ {var}: {'*' * 20}...{valor[-4:]}")
        else:
            print(f"   ❌ {var}: NO CONFIGURADA")
            todas_configuradas = False
    
    return todas_configuradas

def verificar_cuentas_disponibles():
    """Verifica cuentas publicitarias disponibles"""
    print("\n2️⃣ Cuentas publicitarias:")
    try:
        # Obtener cuentas activas
        cuentas = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, estado_actual, webhook_registrado') \
            .eq('estado_actual', 'ACTIVE') \
            .execute()
        
        if cuentas.data:
            print(f"   📊 Total cuentas activas: {len(cuentas.data)}")
            
            sin_webhook = [c for c in cuentas.data if not c.get('webhook_registrado', False)]
            con_webhook = len(cuentas.data) - len(sin_webhook)
            
            print(f"   ✅ Con webhook: {con_webhook}")
            print(f"   ⏳ Sin webhook: {len(sin_webhook)}")
            
            if sin_webhook:
                print("\n   📋 Cuentas sin webhook:")
                for cuenta in sin_webhook[:5]:  # Mostrar solo 5
                    nombre = cuenta.get('nombre_cliente', 'Sin nombre')
                    id_cuenta = cuenta['id_cuenta_publicitaria']
                    print(f"      • {nombre} ({id_cuenta})")
                
                if len(sin_webhook) > 5:
                    print(f"      ... y {len(sin_webhook) - 5} más")
            
            return len(sin_webhook) > 0
        else:
            print("   ❌ No hay cuentas activas")
            return False
            
    except Exception as e:
        print(f"   ❌ Error consultando cuentas: {e}")
        return False

def verificar_tabla_logs():
    """Verifica que la tabla logs_webhooks_meta esté lista"""
    print("\n3️⃣ Tabla logs_webhooks_meta:")
    try:
        # Test básico de inserción/borrado
        test_data = {
            'tipo_objeto': 'test',
            'objeto_id': 'test_123',
            'campo': 'test_field',
            'valor': 'test_value'
        }
        
        # Insertar
        result = supabase.table('logs_webhooks_meta').insert(test_data).execute()
        
        if result.data:
            inserted_id = result.data[0]['id']
            print(f"   ✅ Inserción OK (ID: {inserted_id})")
            
            # Borrar inmediatamente
            supabase.table('logs_webhooks_meta').delete().eq('id', inserted_id).execute()
            print(f"   ✅ Borrado OK")
            
            return True
        else:
            print("   ❌ Error en inserción")
            return False
            
    except Exception as e:
        print(f"   ❌ Error tabla logs: {e}")
        return False

def simular_registro_masivo():
    """Simula el registro masivo (DRY RUN)"""
    print("\n4️⃣ Simulación registro masivo:")
    try:
        # Obtener cuentas que necesitan webhook
        cuentas = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente') \
            .eq('estado_actual', 'ACTIVE') \
            .eq('webhook_registrado', False) \
            .execute()
        
        if cuentas.data:
            print(f"   🎯 Se registrarían webhooks en {len(cuentas.data)} cuentas:")
            
            for cuenta in cuentas.data[:3]:  # Mostrar solo 3
                nombre = cuenta.get('nombre_cliente', 'Sin nombre')
                id_cuenta = cuenta['id_cuenta_publicitaria']
                print(f"      • {nombre} ({id_cuenta})")
            
            if len(cuentas.data) > 3:
                print(f"      ... y {len(cuentas.data) - 3} más")
                
            return True
        else:
            print("   ℹ️ No hay cuentas que necesiten webhook")
            return True
            
    except Exception as e:
        print(f"   ❌ Error simulación: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICACIÓN REGISTRO MASIVO WEBHOOKS META ADS")
    print("=" * 60)
    print("Este script verifica si el botón 'Registrar Todas' funcionará")
    print("=" * 60)
    
    # Verificaciones
    config_ok = verificar_configuracion()
    cuentas_ok = verificar_cuentas_disponibles()
    tabla_ok = verificar_tabla_logs()
    simulacion_ok = simular_registro_masivo()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL:")
    print(f"   Configuración: {'✅ OK' if config_ok else '❌ ERROR'}")
    print(f"   Cuentas disponibles: {'✅ OK' if cuentas_ok else '❌ ERROR'}")
    print(f"   Tabla logs: {'✅ OK' if tabla_ok else '❌ ERROR'}")
    print(f"   Simulación: {'✅ OK' if simulacion_ok else '❌ ERROR'}")
    
    if all([config_ok, tabla_ok, simulacion_ok]):
        print("\n🎉 ¡LISTO! El botón 'Registrar Todas' debería funcionar perfectamente")
        print("\n📍 Pasos para probar:")
        print("   1. Ir a: /panel_cliente/aura/meta_ads/webhooks")
        print("   2. Hacer clic en: '🚀 Registrar Todas'")
        print("   3. Confirmar el diálogo")
        print("   4. Esperar resultado en el log")
        
        if cuentas_ok:
            print("\n💡 Hay cuentas sin webhook - el registro será efectivo")
        else:
            print("\n💡 No hay cuentas sin webhook - el proceso será informativo")
    else:
        print("\n❌ HAY PROBLEMAS - Corregir antes de usar el botón")
        
        if not config_ok:
            print("   • Configurar variables de entorno faltantes")
        if not tabla_ok:
            print("   • Verificar tabla logs_webhooks_meta")

if __name__ == "__main__":
    main()
