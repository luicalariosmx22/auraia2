#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar los logs de webhooks en Supabase
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

def verificar_logs_webhooks():
    """Verifica los logs de webhooks recientes"""
    print("📋 Verificando logs de webhooks en Supabase...")
    
    try:
        # Obtener logs de las últimas 2 horas
        hace_2_horas = (datetime.now() - timedelta(hours=2)).isoformat()
        
        response = supabase.table('logs_webhooks_meta')\
            .select('*')\
            .gte('timestamp', hace_2_horas)\
            .order('timestamp', desc=True)\
            .limit(10)\
            .execute()
        
        if response.data:
            print(f"✅ Encontrados {len(response.data)} eventos recientes:")
            print("-" * 80)
            
            for i, evento in enumerate(response.data, 1):
                print(f"{i}. ID: {evento.get('id')}")
                print(f"   Tipo: {evento.get('tipo_objeto')}")
                print(f"   Objeto ID: {evento.get('objeto_id')}")
                print(f"   Campo: {evento.get('campo')}")
                print(f"   Valor: {evento.get('valor')}")
                print(f"   Timestamp: {evento.get('timestamp')}")
                print("-" * 40)
                
            return True
        else:
            print("❌ No se encontraron eventos recientes")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando logs: {e}")
        return False

def verificar_audiencias_marcadas():
    """Verifica si hay audiencias marcadas para sync"""
    print("\n📊 Verificando audiencias marcadas para sync...")
    
    try:
        response = supabase.table('meta_ads_audiencias')\
            .select('audience_id, nombre, webhook_actualizada, requiere_sync')\
            .eq('requiere_sync', True)\
            .order('webhook_actualizada', desc=True)\
            .limit(5)\
            .execute()
        
        if response.data:
            print(f"✅ Encontradas {len(response.data)} audiencias marcadas para sync:")
            print("-" * 60)
            
            for audiencia in response.data:
                print(f"• ID: {audiencia.get('audience_id')}")
                print(f"  Nombre: {audiencia.get('nombre', 'Sin nombre')}")
                print(f"  Webhook actualizada: {audiencia.get('webhook_actualizada')}")
                print()
                
            return True
        else:
            print("ℹ️ No hay audiencias marcadas para sync actualmente")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando audiencias: {e}")
        return False

def verificar_estadisticas_webhooks():
    """Muestra estadísticas generales de webhooks"""
    print("\n📈 Estadísticas generales de webhooks...")
    
    try:
        # Obtener estadísticas usando la función helper
        from clientes.aura.utils.meta_webhook_helpers import obtener_estadisticas_webhooks
        
        stats = obtener_estadisticas_webhooks()
        
        print("📊 ESTADÍSTICAS:")
        print(f"• Total eventos: {stats.get('total_eventos', 0)}")
        print(f"• Eventos procesados: {stats.get('eventos_procesados', 0)}")
        print(f"• Eventos pendientes: {stats.get('eventos_pendientes', 0)}")
        print(f"• Última actualización: {stats.get('ultima_actualizacion')}")
        
        tipos = stats.get('tipos_objeto', {})
        if tipos:
            print("📋 Por tipo de objeto:")
            for tipo, cantidad in tipos.items():
                print(f"  - {tipo}: {cantidad}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return False

def main():
    """Ejecutar todas las verificaciones"""
    print("🔍 VERIFICANDO FUNCIONAMIENTO DE WEBHOOKS")
    print("=" * 60)
    
    # Verificar logs
    logs_ok = verificar_logs_webhooks()
    
    # Verificar audiencias marcadas
    audiencias_ok = verificar_audiencias_marcadas()
    
    # Verificar estadísticas
    stats_ok = verificar_estadisticas_webhooks()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN:")
    print(f"✅ Logs de webhooks: {'OK' if logs_ok else 'Sin eventos recientes'}")
    print(f"✅ Audiencias marcadas: {'OK' if audiencias_ok else 'Ninguna marcada'}")
    print(f"✅ Estadísticas: {'OK' if stats_ok else 'Error'}")
    
    if logs_ok:
        print("\n🎉 ¡El webhook está funcionando y guardando eventos correctamente!")
        print("\n💡 PRÓXIMOS PASOS:")
        print("1. En el Developer Console de Meta, tu webhook ya debería estar verificado")
        print("2. Puedes suscribirte a eventos específicos (ads, campaigns, audiences)")
        print("3. Los cambios en Meta se registrarán automáticamente en tu sistema")
    else:
        print("\n⚠️ El webhook funciona pero no hay eventos recientes registrados")
        print("Esto es normal si acabas de configurarlo")

if __name__ == "__main__":
    main()
