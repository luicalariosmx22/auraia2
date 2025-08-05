"""
Script para verificar las rutas registradas en el blueprint de Meta Ads
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
    
    print("✅ Blueprint importado correctamente")
    print(f"📋 Nombre del blueprint: {panel_cliente_meta_ads_bp.name}")
    print(f"📁 URL prefix: {panel_cliente_meta_ads_bp.url_prefix}")
    
    print("\n📍 Rutas registradas:")
    for rule in panel_cliente_meta_ads_bp.url_map.iter_rules():
        if rule.rule.startswith('/panel_cliente/<nombre_nora>/meta_ads'):
            print(f"  ➡️  {rule.rule} [{', '.join(rule.methods)}] -> {rule.endpoint}")
    
    # Verificar si la ruta específica existe
    target_route = '/panel_cliente/<nombre_nora>/meta_ads/estadisticas/compartir_reporte'
    route_found = False
    for rule in panel_cliente_meta_ads_bp.url_map.iter_rules():
        if 'compartir_reporte' in rule.rule:
            print(f"\n🎯 Ruta de compartir encontrada: {rule.rule}")
            route_found = True
    
    if not route_found:
        print("\n❌ No se encontró la ruta de compartir_reporte")
        
except ImportError as e:
    print(f"❌ Error al importar: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
