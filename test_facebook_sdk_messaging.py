#!/usr/bin/env python3
"""
Script para probar messaging_conversations_started usando Facebook Business SDK
"""

import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_with_facebook_sdk():
    """
    Prueba con el SDK oficial de Facebook Business
    """
    
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.ad import Ad
        print("✅ SDK de Facebook Business importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SDK: {e}")
        print("Instala con: pip install facebook-business")
        return False
    
    # Configuración
    access_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID', 'dummy_app_id')
    app_secret = os.getenv('META_APP_SECRET', 'dummy_secret')
    
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN en .env")
        return False
    
    # Inicializar API
    try:
        FacebookAdsApi.init(app_id, app_secret, access_token)
        print("✅ API inicializada correctamente")
    except Exception as e:
        print(f"❌ Error inicializando API: {e}")
        return False
    
    # Cuenta de prueba
    test_account_id = "88526564"
    
    # Fechas
    fecha_fin = date.today() - timedelta(days=1)
    fecha_inicio = fecha_fin - timedelta(days=7)
    
    print(f"\n🔍 PROBANDO CON FACEBOOK BUSINESS SDK")
    print("="*60)
    print(f"Cuenta: act_{test_account_id}")
    print(f"Período: {fecha_inicio} → {fecha_fin}")
    print()
    
    try:
        # Obtener cuenta publicitaria
        account = AdAccount(f'act_{test_account_id}')
        print(f"✅ Cuenta publicitaria obtenida")
        
        # Obtener anuncios
        print("\n📋 Obteniendo anuncios...")
        ads = account.get_ads(fields=['id', 'name', 'status'])
        ads_list = list(ads)
        print(f"📊 Anuncios encontrados: {len(ads_list)}")
        
        conversations_found = 0
        
        # Probar con los primeros 3 anuncios
        for i, ad in enumerate(ads_list[:3]):
            print(f"\n🎯 Anuncio {i+1}: {ad.get('name', 'Sin nombre')} ({ad.get('id')})")
            
            try:
                # MÉTODO RECOMENDADO: Usar get_insights con campos específicos
                insights = ad.get_insights(
                    fields=[
                        'ad_id',
                        'ad_name',
                        'actions',
                        'spend',
                        'impressions'
                    ],
                    params={
                        'time_range': {
                            'since': fecha_inicio.strftime('%Y-%m-%d'),
                            'until': fecha_fin.strftime('%Y-%m-%d')
                        },
                        'action_attribution_windows': ['7d_click', '1d_view']
                    }
                )
                
                insights_list = list(insights)
                print(f"   📈 Insights obtenidos: {len(insights_list)}")
                
                for insight in insights_list:
                    actions = insight.get('actions', [])
                    print(f"   📋 Acciones encontradas: {len(actions)}")
                    
                    if actions:
                        # Mostrar todas las acciones
                        action_types = [action.get('action_type') for action in actions]
                        print(f"   🔍 Tipos de acciones: {action_types}")
                        
                        # Buscar específicamente conversaciones de mensajería
                        for action in actions:
                            action_type = action.get('action_type', '')
                            value = action.get('value', 0)
                            
                            # Buscar cualquier acción relacionada con messaging
                            if any(keyword in action_type.lower() for keyword in ['messaging', 'conversation', 'message']):
                                print(f"   💬 CONVERSACIÓN ENCONTRADA: {action_type} = {value}")
                                conversations_found += 1
                            
                            # También mostrar otras acciones relevantes
                            if action_type in ['link_click', 'post_engagement', 'video_view']:
                                print(f"   📊 {action_type}: {value}")
                    else:
                        print("   ❌ Sin acciones registradas")
                        
            except Exception as e:
                print(f"   ❌ Error obteniendo insights del anuncio: {e}")
        
        # MÉTODO ALTERNATIVO: Insights a nivel de cuenta
        print(f"\n📋 MÉTODO ALTERNATIVO: Insights de cuenta")
        print("-" * 40)
        
        try:
            account_insights = account.get_insights(
                fields=['actions', 'spend', 'impressions'],
                params={
                    'time_range': {
                        'since': fecha_inicio.strftime('%Y-%m-%d'),
                        'until': fecha_fin.strftime('%Y-%m-%d')
                    },
                    'level': 'ad',
                    'action_attribution_windows': ['7d_click', '1d_view']
                }
            )
            
            account_insights_list = list(account_insights)
            print(f"📊 Insights de cuenta: {len(account_insights_list)}")
            
            messaging_total = 0
            for insight in account_insights_list:
                actions = insight.get('actions', [])
                for action in actions:
                    action_type = action.get('action_type', '')
                    if 'messaging' in action_type.lower():
                        messaging_total += int(action.get('value', 0))
            
            if messaging_total > 0:
                print(f"💬 Total conversaciones en cuenta: {messaging_total}")
            else:
                print("❌ No se encontraron conversaciones a nivel de cuenta")
                
        except Exception as e:
            print(f"❌ Error con insights de cuenta: {e}")
        
        # RESUMEN FINAL
        print(f"\n🎯 RESUMEN FINAL")
        print("="*40)
        print(f"Conversaciones encontradas: {conversations_found}")
        
        if conversations_found == 0:
            print("\n💡 ANÁLISIS:")
            print("✓ SDK configurado correctamente")
            print("✓ Anuncios obtenidos correctamente")
            print("✓ Insights consultados exitosamente")
            print("❌ Pero no se encontraron acciones de mensajería")
            print("\n🔍 POSIBLES CAUSAS:")
            print("- Los anuncios no tienen objetivo de 'Mensajes'")
            print("- No se generaron conversaciones en este período")
            print("- Los anuncios no son Click-to-Message o Click-to-WhatsApp")
            print("- Se necesita configurar los anuncios específicamente para mensajería")
        else:
            print("🎉 ¡Conversaciones encontradas exitosamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    test_with_facebook_sdk()
