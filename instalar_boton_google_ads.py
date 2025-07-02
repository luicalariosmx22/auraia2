#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para añadir el botón de actualización de Google Ads al panel existente
"""

import os
import shutil
import re
from datetime import datetime

def agregar_boton_google_ads():
    """
    Añade el botón de actualización de Google Ads al panel existente
    """
    # Ruta al archivo de template del panel de Google Ads
    template_path = r"c:\Users\PC\PYTHON\AuraAi2\clientes\aura\templates\panel_cliente_google_ads\cuentas.html"
    
    # Verificar que el archivo existe
    if not os.path.exists(template_path):
        print(f"❌ Error: El archivo {template_path} no existe.")
        print("   Por favor, asegúrate de que la ruta es correcta.")
        return False
    
    # Hacer una copia de seguridad del archivo
    backup_path = f"{template_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 Creando copia de seguridad: {backup_path}")
    shutil.copy2(template_path, backup_path)
    
    # Leer el contenido del archivo
    print(f"📄 Leyendo archivo: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Verificar si el botón ya está presente
    if 'google_ads_update_button.js' in content:
        print("⚠️ El botón ya parece estar integrado en el archivo.")
        confirm = input("¿Deseas continuar de todos modos? (s/n): ")
        if confirm.lower() != 's':
            print("❌ Operación cancelada.")
            return False
    
    # Buscar el punto de inserción - idealmente antes de cerrar el bloque de contenido principal
    # pero después de mostrar los datos de las cuentas
    target_patterns = [
        r'(<!-- Contenido principal -->.*?)(</div>\s*<!-- Fin contenido principal -->)',
        r'(<!-- Tabla de cuentas -->.*?)(</div>\s*<!-- Fin tabla de cuentas -->)',
        r'(<div class="card-body">.*?)(\s*</div>\s*</div>\s*</div>)'
    ]
    
    insertion_point = None
    for pattern in target_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            insertion_point = match.span(2)[0]
            break
    
    if not insertion_point:
        print("⚠️ No se encontró un punto adecuado para insertar el botón.")
        print("   Insertando el botón al final del body como alternativa.")
        insertion_point = content.find('</body>')
        if insertion_point == -1:
            print("❌ Error: No se encontró el tag </body>.")
            return False
    
    # Preparar el código HTML para el botón
    button_html = '''
    <!-- Inicio - Botón de actualización de Google Ads -->
    <div class="card mt-4">
        <div class="card-header bg-primary text-white">
            <i class="fas fa-sync-alt me-2"></i>
            Actualización Manual
        </div>
        <div class="card-body">
            <p>
                Los datos se actualizan automáticamente cada semana, pero puedes obtener las métricas 
                de los últimos 7 días manualmente con el siguiente botón:
            </p>
            <div id="google-ads-update-container" class="mb-3">
                <!-- El botón se generará aquí mediante JavaScript -->
            </div>
        </div>
    </div>
    <!-- Fin - Botón de actualización de Google Ads -->
    '''
    
    # Preparar el código JavaScript para inicializar el botón
    button_js = '''
<!-- Inicializar botón de actualización de Google Ads -->
<script src="/static/js/components/google_ads_update_button.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Inicializar el botón de actualización
        const updateButton = new GoogleAdsUpdateButton('google-ads-update-container');
    });
</script>
'''
    
    # Insertar el HTML del botón
    new_content = content[:insertion_point] + button_html + content[insertion_point:]
    
    # Insertar el JavaScript antes del cierre del body
    js_insertion_point = new_content.find('</body>')
    if js_insertion_point != -1:
        new_content = new_content[:js_insertion_point] + button_js + new_content[js_insertion_point:]
    
    # Guardar el archivo modificado
    print(f"💾 Guardando cambios en: {template_path}")
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("✅ ¡Botón añadido correctamente!")
    print("   Ahora puedes acceder a la página para ver el botón:")
    print("   http://localhost:5000/panel_cliente/aura/google_ads/cuentas")
    return True

if __name__ == "__main__":
    print("="*80)
    print("🔧 INSTALACIÓN DE BOTÓN DE GOOGLE ADS")
    print("="*80)
    
    # Verificar que existe el directorio para el componente JavaScript
    js_dir = r"c:\Users\PC\PYTHON\AuraAi2\static\js\components"
    if not os.path.exists(js_dir):
        print(f"📁 Creando directorio: {js_dir}")
        os.makedirs(js_dir, exist_ok=True)
    
    # Verificar que existe el archivo JavaScript del botón
    js_file = os.path.join(js_dir, "google_ads_update_button.js")
    if not os.path.exists(js_file):
        print(f"❌ Error: El archivo {js_file} no existe.")
        print("   Por favor, asegúrate de que el archivo ha sido creado correctamente.")
        exit(1)
    
    # Añadir el botón al panel
    agregar_boton_google_ads()
    
    print("="*80)
