#!/usr/bin/env python3
"""
Script para probar la captura de messaging_conversations_started
usando diferentes enfoques de la API de Meta
"""

import os
import requests
import json
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_messaging_with_graph_api():
    """
    Método 1: Usar Graph API directamente (actual)
    """
    print("="*60)
    print("🔍 MÉTODO 1: Graph API Directa (requests)")
    print("="*60)
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    test_account_id = "88526564"
    
    fecha_fin = date.today() - timedelta(days=1)
    fecha_inicio = fecha_fin - timedelta(days=30)  # 30 días para más datos
    
    url = f"https://graph.facebook.com/v19.0/act_{test_account_id}/insights"
    
    params = {
        'access_token': access_token,
        'level': 'ad',
        'fields': 'ad_id,ad_name,actions',
        'action_attribution_windows': ['1d_view', '7d_click', '28d_click'],
        'time_range': json.dumps({
            'since': fecha_inicio.strftime('%Y-%m-%d'),
            'until': fecha_fin.strftime('%Y-%m-%d')
        }),
        'limit': 20
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        insights = data.get('data', [])
        
        print(f"📊 Insights encontrados: {len(insights)}")
        
        messaging_found = False
        for insight in insights:
            ad_id = insight.get('ad_id')
            actions = insight.get('actions', [])
            
            if actions:
                messaging_actions = [a for a in actions if 'messaging' in a.get('action_type', '').lower()]
                if messaging_actions:
                    messaging_found = True
                    print(f"💬 Anuncio {ad_id}: {messaging_actions}")
                else:
                    # Mostrar todas las acciones para debug
                    all_actions = [a.get('action_type') for a in actions]
                    print(f"📋 Anuncio {ad_id}: {all_actions}")
        
        if not messaging_found:
            print("❌ No se encontraron acciones de messaging en Graph API")
            
    except Exception as e:
        print(f"❌ Error con Graph API: {e}")


def test_messaging_with_facebook_business_sdk():
    """
    Método 2: Usar Facebook Business SDK
    """
    print("\n" + "="*60)
    print("🔍 MÉTODO 2: Facebook Business SDK")
    print("="*60)
    
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.adsinsights import AdsInsights
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        app_id = os.getenv('META_APP_ID', 'your-app-id')
        app_secret = os.getenv('META_APP_SECRET', 'your-app-secret')
        
        # Inicializar API
        FacebookAdsApi.init(app_id, app_secret, access_token)
        
        test_account_id = "88526564"
        account = AdAccount(f'act_{test_account_id}')
        
        fecha_fin = date.today() - timedelta(days=1)
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Consultar insights con SDK
        try:
            insights = account.get_insights(
                fields=[
                    AdsInsights.Field.ad_id,
                    AdsInsights.Field.ad_name,
                    AdsInsights.Field.actions,
                ],
                params={
                    'level': 'ad',
                    'time_range': {
                        'since': fecha_inicio.strftime('%Y-%m-%d'),
                        'until': fecha_fin.strftime('%Y-%m-%d')
                    },
                    'action_attribution_windows': ['1d_view', '7d_click', '28d_click'],
                    'limit': 20
                }
            )
            
            print("📊 Consultando insights con SDK...")
            
            messaging_found = False
            insight_count = 0
            
            # Iterar usando el cursor del SDK
            for insight in insights:
                insight_count += 1
                ad_id = insight.get('ad_id')
                actions = insight.get('actions', [])
                
                if actions:
                    messaging_actions = [a for a in actions if 'messaging' in a.get('action_type', '').lower()]
                    if messaging_actions:
                        messaging_found = True
                        print(f"💬 SDK Anuncio {ad_id}: {messaging_actions}")
                    else:
                        all_actions = [a.get('action_type') for a in actions]
                        print(f"📋 SDK Anuncio {ad_id}: {all_actions[:5]}...")  # Solo primeras 5
            
            print(f"📊 Total insights procesados: {insight_count}")
            
            if not messaging_found:
                print("❌ No se encontraron acciones de messaging con SDK")
                
        except Exception as sdk_error:
            print(f"❌ Error en consulta SDK: {sdk_error}")
            
    except ImportError:
        print("❌ Facebook Business SDK no está instalado")
        print("   Instalar con: pip install facebook_business")
    except Exception as e:
        print(f"❌ Error con Facebook Business SDK: {e}")


def test_messaging_with_page_insights():
    """
    Método 3: Usar Page Insights (tu ejemplo)
    """
    print("\n" + "="*60)
    print("🔍 MÉTODO 3: Page Messaging Insights")
    print("="*60)
    
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.page import Page
        from facebook_business.adobjects.messaginginsights import MessagingInsights
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        app_id = os.getenv('META_APP_ID', 'your-app-id')
        app_secret = os.getenv('META_APP_SECRET', 'your-app-secret')
        page_id = os.getenv('META_PAGE_ID', 'your-page-id')  # Necesitas el PAGE_ID
        
        # Inicializar API
        FacebookAdsApi.init(app_id, app_secret, access_token)
        
        if page_id and page_id != 'your-page-id':
            page = Page(page_id)
            insights = page.get_messaging_insights(
                fields=[MessagingInsights.Field.conversations_started],
                params={
                    'since': '2025-01-01', 
                    'until': '2025-01-31'
                }
            )
            
            print(f"📊 Page Messaging Insights: {list(insights)}")
        else:
            print("⚠️ PAGE_ID no configurado en variables de entorno")
            
    except ImportError:
        print("❌ Facebook Business SDK no está instalado")
    except Exception as e:
        print(f"❌ Error con Page Messaging Insights: {e}")


def test_extended_attribution_windows():
    """
    Método 4: Probar ventanas de atribución extendidas
    """
    print("\n" + "="*60)
    print("🔍 MÉTODO 4: Ventanas de Atribución Extendidas")
    print("="*60)
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    test_account_id = "88526564"
    
    fecha_fin = date.today() - timedelta(days=1)
    fecha_inicio = fecha_fin - timedelta(days=7)
    
    # Diferentes ventanas de atribución para messaging
    attribution_windows = [
        ['1d_view', '1d_click'],
        ['7d_view', '7d_click'], 
        ['28d_view', '28d_click'],
        ['1d_view', '7d_click', '28d_click']
    ]
    
    for i, windows in enumerate(attribution_windows, 1):
        print(f"\n🔬 Prueba {i}: Ventanas {windows}")
        
        url = f"https://graph.facebook.com/v19.0/act_{test_account_id}/insights"
        
        params = {
            'access_token': access_token,
            'level': 'ad',
            'fields': 'ad_id,actions',
            'action_attribution_windows': windows,
            'time_range': json.dumps({
                'since': fecha_inicio.strftime('%Y-%m-%d'),
                'until': fecha_fin.strftime('%Y-%m-%d')
            }),
            'limit': 5
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            insights = data.get('data', [])
            
            messaging_count = 0
            for insight in insights:
                actions = insight.get('actions', [])
                for action in actions:
                    if 'messaging' in action.get('action_type', '').lower():
                        messaging_count += 1
                        print(f"   💬 {action.get('action_type')}: {action.get('value')}")
            
            if messaging_count == 0:
                print(f"   ❌ Sin messaging con ventanas {windows}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """
    Ejecutar todas las pruebas
    """
    print("🧪 TESTING MESSAGING CONVERSATIONS STARTED")
    print("==========================================")
    
    # Verificar token
    access_token = os.getenv('META_ACCESS_TOKEN')
    if not access_token:
        print("❌ META_ACCESS_TOKEN no encontrado en variables de entorno")
        return
    
    print(f"✅ Token configurado: {access_token[:20]}...")
    
    # Ejecutar todas las pruebas
    test_messaging_with_graph_api()
    test_messaging_with_facebook_business_sdk()
    test_messaging_with_page_insights()
    test_extended_attribution_windows()
    
    print("\n" + "="*60)
    print("🎯 CONCLUSIONES Y RECOMENDACIONES:")
    print("="*60)
    print("1. Si no hay datos de messaging, puede ser que:")
    print("   - Los anuncios no están configurados para generar mensajes")
    print("   - No hay campañas Click-to-Messenger activas")
    print("   - El período consultado no tiene actividad de messaging")
    print("2. Verifica que META_PAGE_ID esté configurado para Method 3")
    print("3. Prueba con diferentes ventanas de atribución")
    print("4. Considera usar Facebook Business SDK en lugar de requests")


if __name__ == "__main__":
    main()
