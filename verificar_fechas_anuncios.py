#!/usr/bin/env python3
import sys
sys.path.append('.')
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime

# Verificar datos disponibles para la semana del 4-10 agosto
print('🔍 Verificando datos en meta_ads_anuncios_detalle para semana 4-10 agosto 2025...')
result = supabase.table('meta_ads_anuncios_detalle').select('fecha_inicio, fecha_fin').gte('fecha_inicio', '2025-08-04').lte('fecha_fin', '2025-08-10').execute()

if result.data:
    print(f'✅ Encontrados {len(result.data)} registros para esa semana')
    fechas_unicas = set()
    for item in result.data:
        fechas_unicas.add(f"{item['fecha_inicio']} to {item['fecha_fin']}")
    print('📅 Rangos de fechas únicos encontrados:')
    for fecha in sorted(fechas_unicas):
        print(f'   - {fecha}')
else:
    print('❌ No hay datos para la semana del 4-10 agosto')
    
    # Veamos qué datos hay disponibles
    print('\n🔍 Verificando todos los datos disponibles...')
    all_data = supabase.table('meta_ads_anuncios_detalle').select('fecha_inicio, fecha_fin').limit(20).execute()
    if all_data.data:
        fechas_todas = set()
        for item in all_data.data[:10]:  # Solo mostrar primeros 10
            fechas_todas.add(f"{item['fecha_inicio']} to {item['fecha_fin']}")
        print('📅 Algunas fechas disponibles:')
        for fecha in sorted(fechas_todas):
            print(f'   - {fecha}')

# También verificar reportes existentes
print('\n📊 Verificando reportes existentes en meta_ads_reportes_semanales...')
reportes = supabase.table('meta_ads_reportes_semanales').select('fecha_inicio, fecha_fin, created_at, estatus').order('created_at', desc=True).limit(5).execute()

if reportes.data:
    print(f'✅ Encontrados {len(reportes.data)} reportes recientes:')
    for reporte in reportes.data:
        print(f'   - {reporte["fecha_inicio"]} to {reporte["fecha_fin"]} | Status: {reporte.get("estatus", "N/A")} | Created: {reporte["created_at"][:10]}')
else:
    print('❌ No hay reportes en la tabla')
