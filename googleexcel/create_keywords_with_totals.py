import pandas as pd

# Datos de ejemplo más realistas para palabras clave (incluyendo filas de totales para probar el filtrado)
keywords_data = {
    'Campaign': [
        'Todo el período',  # Fila de total que debe ser filtrada
        'Total: Cuenta',     # Fila de total que debe ser filtrada  
        'Total: Búsqueda',   # Fila de total que debe ser filtrada
        'SaldeJade - Keywords Search',  # Datos reales empiezan aquí
        'SaldeJade - Keywords Search', 
        'SaldeJade - Keywords Search',
        'SaldeJade - Keywords Search',
        'SaldeJade - Keywords Search',
        'Total: Todas las palabras clave, excepto las quitadas'  # Otra fila de total
    ],
    'Ad group': [
        None,
        None,
        None,
        'Restaurante Keywords',
        'Restaurante Keywords',
        'Mixologia Keywords', 
        'Mixologia Keywords',
        'Reservaciones Keywords',
        None
    ],
    'Keyword': [
        None,
        None,
        None,
        'restaurante hermosillo',
        'mejor restaurante hermosillo',
        'mixologia hermosillo',
        'cocteles hermosillo',
        'reservar restaurante hermosillo',
        None
    ],
    'Match type': [
        None,
        'Total: Cuenta',
        'Total: Búsqueda',
        'Exact',
        'Phrase',
        'Exact',
        'Broad',
        'Phrase',
        'Total: Todas las palabras clave, excepto las quitadas'
    ],
    'Keyword state': [
        'Todo el período',
        None,
        None,
        'Enabled',
        'Enabled',
        'Enabled',
        'Paused',
        'Enabled',
        None
    ],
    'Max CPC': [
        None,
        None,
        None,
        2.50,
        1.80,
        3.00,
        2.20,
        1.90,
        None
    ],
    'Final URL': [
        None,
        None,
        None,
        'https://saldejade.mx/',
        'https://saldejade.mx/',
        'https://saldejade.mx/mixologia/',
        'https://saldejade.mx/mixologia/',
        'https://saldejade.mx/reservaciones/',
        None
    ],
    'Impressions': [
        None,
        365379,  # Total
        365379,  # Total
        1250,
        890,
        654,
        423,
        789,
        365352   # Total
    ],
    'Clicks': [
        None,
        28009,   # Total
        28009,   # Total
        98,
        67,
        45,
        12,
        56,
        28009    # Total
    ],
    'CTR': [
        None,
        '0.0767',
        '0.0767',
        '7.84%',
        '7.53%',
        '6.88%',
        '2.84%',
        '7.10%',
        '0.0767'
    ],
    'Avg. CPC': [
        None,
        1.52,    # Total
        1.52,    # Total
        1.85,
        1.42,
        2.15,
        1.98,
        1.23,
        1.52     # Total
    ],
    'Cost': [
        None,
        42592.31, # Total
        42592.31, # Total
        181.30,
        95.14,
        96.75,
        23.76,
        68.88,
        42592.31  # Total
    ],
    'Conversions': [
        None,
        86,      # Total
        86,      # Total
        5,
        3,
        2,
        0,
        4,
        86       # Total
    ],
    'Cost/conv.': [
        None,
        495.26,  # Total
        495.26,  # Total
        36.26,
        31.71,
        48.38,
        0,
        17.22,
        495.26   # Total
    ],
    'Conv. rate': [
        None,
        '0.0031',
        '0.0031',
        '5.10%',
        '4.48%',
        '4.44%',
        '0.00%',
        '7.14%',
        '0.0031'
    ]
}

# Crear DataFrame
df = pd.DataFrame(keywords_data)

# Guardar como Excel
output_file = 'ejemplo_keywords_con_totales.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Archivo de ejemplo creado: {output_file}")
print(f"📊 Datos: {len(df)} filas, {len(df.columns)} columnas")
print(f"🔍 Incluye {df['Keyword'].notna().sum()} palabras clave reales")
print(f"🗑️ Incluye {df['Keyword'].isna().sum()} filas de totales (que serán filtradas)")

print("\n📋 Filas incluidas:")
for i, row in df.iterrows():
    if pd.notna(row['Keyword']):
        print(f"  ✅ Keyword real: {row['Keyword']}")
    else:
        identifier = row['Campaign'] or row['Match type'] or row['Keyword state'] or f"Fila {i+1}"
        print(f"  🗑️ Total/Resumen: {identifier}")

print(f"\n🚀 Usar este archivo para probar:")
print("   1. El filtrado automático de totales")
print("   2. El procesamiento correcto de keywords reales")
print("   3. En http://localhost:5001 seleccionar 'Palabras Clave (18 columnas)'")
