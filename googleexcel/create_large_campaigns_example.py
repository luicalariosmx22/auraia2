#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el generador de campañas con archivos grandes
que puedan causar errores de límite de contexto en OpenAI
"""

import os
import pandas as pd
from datetime import datetime

def create_large_campaigns_example():
    """Crea un archivo de ejemplo con muchas campañas para probar límites"""
    
    # Datos de ejemplo para campañas con todas las columnas posibles
    campaigns_data = []
    
    for i in range(1, 51):  # 50 campañas de ejemplo
        campaign = {
            'Campaign': f'Campaña Google Ads {i}',
            'Campaign ID': f'123456789{i:02d}',
            'Campaign state': 'ENABLED' if i % 3 != 0 else 'PAUSED',
            'Campaign type': 'Search' if i % 2 == 0 else 'Display',
            'Budget': f'{1000 + i * 100}',
            'Budget name': f'Presupuesto {i}',
            'Budget type': 'Daily',
            'Status': 'Active',
            'Bidding strategy': 'Target CPA' if i % 2 == 0 else 'Manual CPC',
            'Bidding strategy type': 'tCPA' if i % 2 == 0 else 'cpc',
            'Target CPA': f'{i * 5}.00' if i % 2 == 0 else '',
            'Target ROAS': f'{i * 0.1:.2f}' if i % 3 == 0 else '',
            'Currency code': 'USD',
            
            # Métricas
            'Impressions': f'{10000 + i * 1000}',
            'Clicks': f'{500 + i * 50}',
            'CTR': f'{(2.5 + i * 0.1):.2f}%',
            'Avg. CPC': f'{(1.5 + i * 0.05):.2f}',
            'Cost': f'{(750 + i * 75):.2f}',
            'Conversions': f'{25 + i * 2}',
            'Cost/conv.': f'{(30 + i * 2):.2f}',
            'Conv. rate': f'{(5 + i * 0.2):.2f}%',
            'Conv. value': f'{(1250 + i * 100):.2f}',
            'Value/conv.': f'{(50 + i):.2f}',
            
            # Columnas adicionales para probar mapeo
            'All conv.': f'{30 + i * 3}',
            'All conv. rate': f'{(6 + i * 0.3):.2f}%',
            'All conv. value': f'{(1500 + i * 150):.2f}',
            'Search Impr. share': f'{(75 + i % 20):.1f}%',
            'Search top IS': f'{(60 + i % 15):.1f}%',
            'Search abs. top IS': f'{(45 + i % 10):.1f}%',
            'Search lost IS (rank)': f'{(10 + i % 5):.1f}%',
            'Search lost IS (budget)': f'{(15 + i % 8):.1f}%',
            
            # Anuncios y keywords
            'Eligible ads': f'{5 + i % 3}',
            'Ad strength': 'Good' if i % 2 == 0 else 'Average',
            'Labels': f'Label{i}, Campaign{i}' if i % 3 == 0 else '',
            
            # Más columnas específicas
            'Campaign subtype': 'Standard' if i % 2 == 0 else 'Smart',
            'Optimization score': f'{(75 + i % 20):.1f}%',
            'Recommendation dismiss': '0',
            'Phone calls': f'{i % 10}',
            'Call impressions': f'{i * 100}',
            'Phone call rate': f'{(i % 5):.2f}%',
            
            # Conversiones específicas
            'Store visits': f'{i * 2}' if i % 5 == 0 else '',
            'Store visit cost': f'{(20 + i):.2f}' if i % 5 == 0 else '',
            'Store visit rate': f'{(3 + i % 3):.2f}%' if i % 5 == 0 else '',
            'Cross-device conv.': f'{i % 8}',
            'New customers': f'{i % 12}',
            'Customer acquisition cost': f'{(45 + i * 3):.2f}',
        }
        
        campaigns_data.append(campaign)
    
    # Agregar algunas filas de totales/resúmenes para probar el filtrado
    total_row = {
        'Campaign': 'Total: Todo el período',
        'Campaign ID': '',
        'Campaign state': '',
        'Campaign type': '',
        'Budget': '',
        'Budget name': '',
        'Budget type': '',
        'Status': '',
        'Bidding strategy': '',
        'Bidding strategy type': '',
        'Target CPA': '',
        'Target ROAS': '',
        'Currency code': 'USD',
        'Impressions': '750000',
        'Clicks': '37500',
        'CTR': '5.00%',
        'Avg. CPC': '$2.00',
        'Cost': '$75,000.00',
        'Conversions': '1500',
        'Cost/conv.': '$50.00',
        'Conv. rate': '4.00%',
        'Conv. value': '$150,000.00',
        'Value/conv.': '$100.00',
    }
    
    campaigns_data.append(total_row)
    
    # Crear DataFrame
    df = pd.DataFrame(campaigns_data)
    
    # Guardar como Excel
    filename = f'ejemplo_campañas_grandes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join('.', filename)
    df.to_excel(filepath, index=False)
    
    print(f"✅ Archivo de ejemplo creado: {filename}")
    print(f"📊 Datos: {len(campaigns_data)} filas, {len(df.columns)} columnas")
    print(f"📁 Ubicación: {filepath}")
    
    return filepath

if __name__ == "__main__":
    print("🧪 Generando archivo de ejemplo para probar campañas grandes...")
    file_path = create_large_campaigns_example()
    print(f"\n🎯 Archivo listo para probar en: {file_path}")
    print("📋 Puedes usar este archivo en el sistema web para probar:")
    print("   1. El generador simple (siempre funciona)")
    print("   2. El generador IA (con fallback automático si excede límites)")
