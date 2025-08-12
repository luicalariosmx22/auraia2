#!/usr/bin/env python3
"""
Script de prueba para verificar si el blueprint de agenda está configurado correctamente
para servir archivos estáticos
"""

import os
import sys

def test_blueprint_static_config():
    """Verifica la configuración de archivos estáticos del blueprint"""
    print("🔍 VERIFICANDO CONFIGURACIÓN BLUEPRINT AGENDA")
    print("=" * 60)
    
    # 1. Verificar estructura de archivos
    print("\n1. 📁 Verificando estructura de archivos:")
    
    agenda_route_file = "clientes/aura/routes/panel_cliente_agenda/panel_cliente_agenda.py"
    template_file = "clientes/aura/templates/panel_cliente_agenda/index.html"
    css_file = "clientes/aura/static/css/modulos/agenda/main.css"
    js_file = "clientes/aura/static/js/modulos/agenda/main.js"
    
    files_to_check = [
        (agenda_route_file, "Blueprint principal"),
        (template_file, "Template principal"),
        (css_file, "Archivo CSS"),
        (js_file, "Archivo JavaScript")
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {description}: {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {description}: {file_path} - NO ENCONTRADO")
    
    # 2. Verificar configuración del blueprint
    print("\n2. ⚙️ Verificando configuración del blueprint:")
    
    try:
        with open(agenda_route_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'static_folder=' in content:
            print("   ✅ Blueprint tiene configuración de static_folder")
            
            # Extraer la configuración
            import re
            static_config = re.search(r'static_folder=[\'\"](.*?)[\'\"]', content)
            if static_config:
                static_path = static_config.group(1)
                print(f"   📂 Ruta configurada: {static_path}")
                
                # Verificar que la ruta sea correcta
                expected_path = "../../static"
                if static_path == expected_path:
                    print(f"   ✅ Ruta correcta: apunta a clientes/aura/static/")
                else:
                    print(f"   ⚠️ Ruta inesperada. Esperada: {expected_path}")
            else:
                print("   ❌ No se pudo extraer la configuración de static_folder")
        else:
            print("   ❌ Blueprint NO tiene configuración de static_folder")
            
    except Exception as e:
        print(f"   ❌ Error leyendo blueprint: {e}")
    
    # 3. Verificar referencias en template
    print("\n3. 🖼️ Verificando referencias en template:")
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Verificar referencias CSS
        if "panel_cliente_agenda_bp.static" in template_content:
            print("   ✅ Template usa referencias específicas del blueprint")
            
            if "css/modulos/agenda/main.css" in template_content:
                print("   ✅ Referencia CSS encontrada")
            else:
                print("   ❌ Referencia CSS no encontrada")
                
            if "js/modulos/agenda/main.js" in template_content:
                print("   ✅ Referencia JS encontrada")
            else:
                print("   ❌ Referencia JS no encontrada")
        else:
            print("   ❌ Template NO usa referencias específicas del blueprint")
            
            # Verificar si usa referencias genéricas
            if "url_for('static'" in template_content:
                print("   ⚠️ Template usa url_for('static') genérico")
            
    except Exception as e:
        print(f"   ❌ Error leyendo template: {e}")
    
    # 4. Verificar rutas resultantes
    print("\n4. 🌐 URLs resultantes esperadas:")
    print("   📄 Template: /panel_cliente/aura/agenda/")
    print("   🎨 CSS: /panel_cliente/aura/agenda/static/css/modulos/agenda/main.css")
    print("   📜 JS: /panel_cliente/aura/agenda/static/js/modulos/agenda/main.js")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("\n💡 SIGUIENTE PASO:")
    print("   1. Reiniciar servidor de desarrollo")
    print("   2. Acceder a: http://localhost:5000/panel_cliente/aura/agenda/")
    print("   3. Verificar en DevTools si se cargan CSS y JS")

if __name__ == "__main__":
    test_blueprint_static_config()
