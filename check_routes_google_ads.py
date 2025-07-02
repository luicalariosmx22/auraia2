#!/usr/bin/env python3
"""
Script para verificar las rutas registradas del blueprint Google Ads
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, '/c/Users/PC/PYTHON/AuraAi2')

def main():
    try:
        # Importar la app
        from run import app
        
        print("🔍 VERIFICANDO RUTAS REGISTRADAS")
        print("=" * 50)
        
        # Obtener todas las rutas
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'google_ads' in rule.rule:
                    print(f"✅ {rule.rule} -> {rule.endpoint}")
        
        print("\n🔍 VERIFICANDO BLUEPRINTS")
        print("=" * 30)
        for name, blueprint in app.blueprints.items():
            if 'google_ads' in name:
                print(f"✅ Blueprint: {name}")
                print(f"   Prefix: {blueprint.url_prefix}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
