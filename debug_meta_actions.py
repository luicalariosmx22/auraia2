#!/usr/bin/env python3
"""
Script de debug para verificar qué acciones están disponibles en Meta Ads API
"""

import os
import requests
import json
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def debug_meta_actions():
    """
    Consulta una cuenta específica para ver qué tipos de acciones están disponibles
    """
    access_token = os.getenv('META_ACCESS_TOKEN')
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    # Usar cuenta de prueba proporcionada
    test_account_id = "88526564"
    
    # Fechas de prueba
    fecha_fin = date.today() - timedelta(days=1)
    fecha_inicio = fecha_fin - timedelta(days=7)
    
    url = f"https://graph.facebook.com/v19.0/act_{test_account_id}/insights"
    
    params = {
        'access_token': access_token,
        'level': 'ad',
        'fields': 'ad_id,ad_name,actions',
        'action_attribution_windows': ['1d_view', '7d_click'],
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
        
        print(f"🔍 ANÁLISIS DE ACCIONES DISPONIBLES")
        print("="*60)
        print(f"Cuenta: {test_account_id}")
        print(f"Período: {fecha_inicio} → {fecha_fin}")
        print(f"Insights encontrados: {len(insights)}")
        print()
        
        all_action_types = set()
        
        for i, insight in enumerate(insights[:3]):  # Solo los primeros 3
            print(f"📋 Insight {i+1} - Anuncio: {insight.get('ad_id')}")
            actions = insight.get('actions', [])
            
            if actions:
                print(f"   Acciones encontradas: {len(actions)}")
                for action in actions:
                    action_type = action.get('action_type')
                    value = action.get('value')
                    all_action_types.add(action_type)
                    
                    if 'messaging' in action_type.lower():
                        print(f"   💬 {action_type}: {value}")
                    else:
                        print(f"   📊 {action_type}: {value}")
            else:
                print("   ❌ Sin acciones")
            print()
        
        print("🎯 RESUMEN DE TIPOS DE ACCIONES ENCONTRADAS:")
        print("-" * 50)
        for action_type in sorted(all_action_types):
            emoji = "💬" if 'messaging' in action_type.lower() else "📊"
            print(f"{emoji} {action_type}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_meta_actions()
