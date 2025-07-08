#!/usr/bin/env python3
# Test simple para verificar las rutas de Google Ads

print("🧪 Verificando que los templates existan...")

import os

templates_path = "clientes/aura/templates/panel_cliente_google_ads/"
templates_requeridos = [
    "index.html",
    "cuentas_publicitarias_google_ads.html", 
    "campanas_google_ads.html",
    "reportes_google_ads.html",
    "campanas_activas_google_ads.html"
]

for template in templates_requeridos:
    template_path = os.path.join(templates_path, template)
    if os.path.exists(template_path):
        print(f"✅ {template}")
    else:
        print(f"❌ {template} - NO EXISTE")

print("\n🔍 Verificando rutas en blueprint...")

# Verificar que las funciones existan en el blueprint
import sys
sys.path.insert(0, '.')

try:
    from clientes.aura.routes.panel_cliente_google_ads import panel_cliente_google_ads_bp
    
    rutas_esperadas = [
        ('/', 'panel_google_ads'),
        ('/cuentas_publicitarias', 'vista_cuentas_publicitarias_google_ads'),
        ('/reportes', 'vista_reportes_google_ads'),
        ('/campanas', 'vista_campanas_google_ads'),
        ('/campanas_activas_google_ads', 'campanas_activas_google_ads'),
        ('/actualizar_empresa', 'actualizar_empresa')
    ]
    
    print(f"Blueprint: {panel_cliente_google_ads_bp.name}")
    
    # Verificar que las rutas estén registradas
    rutas_registradas = []
    for rule in panel_cliente_google_ads_bp.url_map.iter_rules() if hasattr(panel_cliente_google_ads_bp, 'url_map') else []:
        rutas_registradas.append(rule.rule)
    
    print(f"Rutas encontradas en blueprint: {len(rutas_registradas)}")
    
    for ruta, funcion in rutas_esperadas:
        # Verificar que la función exista en el blueprint
        if hasattr(panel_cliente_google_ads_bp, 'view_functions'):
            endpoint = f'{panel_cliente_google_ads_bp.name}.{funcion}'
            if endpoint in panel_cliente_google_ads_bp.view_functions:
                print(f"✅ {ruta} → {funcion}")
            else:
                print(f"❌ {ruta} → {funcion} - FUNCIÓN NO ENCONTRADA")
        else:
            print(f"⚠️ {ruta} → {funcion} - NO SE PUEDE VERIFICAR")
    
    print("✅ Blueprint importado correctamente")
    
except Exception as e:
    print(f"❌ Error importando blueprint: {e}")

print("\n🏁 Verificación completada")
print("Ahora puedes probar: http://localhost:5000/panel_cliente/aura/google_ads/")
