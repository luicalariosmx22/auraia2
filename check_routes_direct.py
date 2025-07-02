#!/usr/bin/env python3
"""
Script para verificar que las rutas de Google Ads se registren correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask
    from clientes.aura.routes.panel_cliente_google_ads import panel_cliente_google_ads_bp
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    
    # Registrar el blueprint directamente
    print("🧪 Registrando blueprint de Google Ads...")
    app.register_blueprint(panel_cliente_google_ads_bp, url_prefix="/panel_cliente")
    
    print("📝 Rutas registradas:")
    google_routes = []
    for rule in app.url_map.iter_rules():
        route_str = f"{rule.rule} -> {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]"
        if 'google_ads' in rule.rule or 'google_ads' in rule.endpoint:
            google_routes.append(route_str)
            print(f"  ✅ {route_str}")
    
    if not google_routes:
        print("  ❌ No se encontraron rutas de Google Ads")
        print("\n🔍 Todas las rutas registradas:")
        for rule in app.url_map.iter_rules():
            print(f"  - {rule.rule} -> {rule.endpoint}")
    
    print(f"\n📊 Total de rutas de Google Ads: {len(google_routes)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
