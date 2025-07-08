#!/usr/bin/env python3
"""
Demo de la nueva funcionalidad de múltiples archivos + Supabase
"""

import pandas as pd
import os
from datetime import datetime

def create_demo_files():
    """Crea archivos de ejemplo para demostrar la funcionalidad completa"""
    
    print("🎯 CREANDO ARCHIVOS DE DEMO PARA SUPABASE")
    print("=" * 50)
    
    # Datos de campañas con jerarquía
    campaigns_data = {
        'Campaign': ['SaldeJade - Search Premium', 'SaldeJade - Display Retargeting', 'SaldeJade - Shopping'],
        'Campaign type': ['Search', 'Display', 'Shopping'],
        'Campaign state': ['Enabled', 'Enabled', 'Paused'],
        'Budget': [2500.00, 1500.00, 800.00],
        'Bidding strategy': ['Target CPA', 'Target ROAS', 'Manual CPC'],
        'Target CPA': [45.00, None, None],
        'Target ROAS': [None, 4.5, None],
        'Impressions': [25000, 18500, 5200],
        'Clicks': [750, 320, 85],
        'CTR': ['3.00%', '1.73%', '1.63%'],
        'Cost': [1125.50, 580.30, 127.50],
        'Conversions': [25, 12, 3],
        'Cost/conv.': [45.02, 48.36, 42.50],
        'Conv. rate': ['3.33%', '3.75%', '3.53%']
    }
    
    # Datos de anuncios relacionados con las campañas
    ads_data = {
        'Campaign': [
            'SaldeJade - Search Premium', 'SaldeJade - Search Premium', 'SaldeJade - Search Premium',
            'SaldeJade - Display Retargeting', 'SaldeJade - Display Retargeting',
            'SaldeJade - Shopping', 'SaldeJade - Shopping'
        ],
        'Ad group': [
            'Jade Natural', 'Jade Premium', 'Jade Premium',
            'Audience Remarketing', 'Audience Remarketing',
            'Jade Products', 'Jade Products'
        ],
        'Headline 1': [
            'Jade Natural Auténtico', 'Jade Premium Collection', 'Joyería de Jade Exclusiva',
            'Vuelve por tu Jade', 'Oferta Especial Jade',
            'Compra Jade Online', 'Jade de Calidad'
        ],
        'Headline 2': [
            'Envío Gratis Hoy', 'Calidad Garantizada', 'Descuento 25%',
            '20% Descuento', 'Últimas Piezas',
            'Mejor Precio', 'Stock Limitado'
        ],
        'Description': [
            'Jade natural certificado con envío gratis',
            'Colección premium de jade auténtico',
            'Joyería exclusiva de jade, descuento especial',
            'Regresa y obtén 20% de descuento en jade',
            'Últimas oportunidades en jade premium',
            'Compra jade online con la mejor calidad',
            'Jade auténtico con stock limitado'
        ],
        'Final URL': [
            'https://salde.com/jade-natural',
            'https://salde.com/jade-premium',
            'https://salde.com/joyeria-jade',
            'https://salde.com/remarketing-jade',
            'https://salde.com/oferta-jade',
            'https://salde.com/shopping-jade',
            'https://salde.com/jade-calidad'
        ],
        'Ad type': [
            'Responsive search ad', 'Responsive search ad', 'Responsive search ad',
            'Responsive display ad', 'Responsive display ad',
            'Product Shopping ad', 'Product Shopping ad'
        ],
        'Status': ['Enabled', 'Enabled', 'Enabled', 'Enabled', 'Paused', 'Enabled', 'Enabled'],
        'Impressions': [8500, 7200, 6800, 9200, 4100, 2800, 1950],
        'Clicks': [255, 210, 195, 180, 75, 45, 35],
        'CTR': ['3.00%', '2.92%', '2.87%', '1.96%', '1.83%', '1.61%', '1.79%'],
        'Cost': [382.50, 315.00, 292.50, 270.00, 112.50, 67.50, 52.50],
        'Conversions': [8, 7, 6, 5, 2, 1, 1],
        'Cost/conv.': [47.81, 45.00, 48.75, 54.00, 56.25, 67.50, 52.50]
    }
    
    # Datos de palabras clave relacionadas
    keywords_data = {
        'Campaign': [
            'SaldeJade - Search Premium', 'SaldeJade - Search Premium', 'SaldeJade - Search Premium',
            'SaldeJade - Search Premium', 'SaldeJade - Search Premium', 'SaldeJade - Search Premium',
            'SaldeJade - Shopping', 'SaldeJade - Shopping'
        ],
        'Ad group': [
            'Jade Natural', 'Jade Natural', 'Jade Premium',
            'Jade Premium', 'Jade Premium', 'Jade Premium',
            'Jade Products', 'Jade Products'
        ],
        'Keyword': [
            'jade natural', 'comprar jade natural', 'jade premium auténtico',
            'joyería jade premium', 'jade de calidad', 'jade certificado',
            'jade online', 'comprar jade'
        ],
        'Match type': [
            'Broad match', 'Phrase match', 'Exact match',
            'Phrase match', 'Broad match', 'Exact match',
            'Broad match', 'Phrase match'
        ],
        'Status': ['Enabled', 'Enabled', 'Enabled', 'Enabled', 'Enabled', 'Paused', 'Enabled', 'Enabled'],
        'Final URL': [
            'https://salde.com/jade-natural',
            'https://salde.com/comprar-jade-natural',
            'https://salde.com/jade-premium-autentico',
            'https://salde.com/joyeria-jade-premium',
            'https://salde.com/jade-calidad',
            'https://salde.com/jade-certificado',
            'https://salde.com/jade-online',
            'https://salde.com/comprar-jade'
        ],
        'Impressions': [4200, 3800, 3600, 3100, 2800, 2400, 1800, 1200],
        'Clicks': [126, 114, 108, 93, 84, 60, 36, 24],
        'CTR': ['3.00%', '3.00%', '3.00%', '3.00%', '3.00%', '2.50%', '2.00%', '2.00%'],
        'Cost': [189.00, 171.00, 162.00, 139.50, 126.00, 90.00, 54.00, 36.00],
        'Conversions': [4, 4, 3, 3, 3, 2, 1, 1],
        'Cost/conv.': [47.25, 42.75, 54.00, 46.50, 42.00, 45.00, 54.00, 36.00]
    }
    
    # Crear DataFrames
    campaigns_df = pd.DataFrame(campaigns_data)
    ads_df = pd.DataFrame(ads_data)
    keywords_df = pd.DataFrame(keywords_data)
    
    # Crear archivos Excel
    campaigns_file = 'demo_campaigns.xlsx'
    ads_file = 'demo_ads.xlsx'
    keywords_file = 'demo_keywords.xlsx'
    
    campaigns_df.to_excel(campaigns_file, index=False)
    ads_df.to_excel(ads_file, index=False)
    keywords_df.to_excel(keywords_file, index=False)
    
    print(f"✅ {campaigns_file}: {len(campaigns_df)} campañas creadas")
    print(f"✅ {ads_file}: {len(ads_df)} anuncios creados")
    print(f"✅ {keywords_file}: {len(keywords_df)} palabras clave creadas")
    print()
    print("🌐 Ahora puedes:")
    print("1. Ir a http://localhost:5001")
    print("2. Seleccionar 'Múltiples Archivos + Supabase'")
    print("3. Subir los 3 archivos creados")
    print("4. Hacer clic en 'Procesar Todos los Archivos'")
    print("5. Hacer clic en 'Insertar a Supabase'")
    print()
    print("🔗 Los datos mantendrán las relaciones jerárquicas:")
    print("   📈 Campañas → 📂 Grupos de Anuncios → 📺 Anuncios / 🔑 Palabras Clave")
    
    return campaigns_file, ads_file, keywords_file

if __name__ == "__main__":
    create_demo_files()
