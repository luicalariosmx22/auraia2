#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para añadir el botón de actualización de Google Ads al panel existente
"""

import os
import shutil
import re
from datetime import datetime

# Ruta al archivo de template del panel de Google Ads
template_path = r"c:\Users\PC\PYTHON\AuraAi2\clientes\aura\templates\panel_cliente_google_ads\cuentas.html"

# Verificar que el archivo existe
print(f"Verificando si existe: {template_path}")
if os.path.exists(template_path):
    print("✅ El archivo existe")
else:
    print("❌ El archivo no existe")
    exit(1)

# Hacer una copia de seguridad del archivo
backup_path = f"{template_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"Creando copia de seguridad: {backup_path}")
shutil.copy2(template_path, backup_path)
print("✅ Copia de seguridad creada")

# Leer el contenido del archivo
print(f"Leyendo archivo: {template_path}")
with open(template_path, 'r', encoding='utf-8') as file:
    content = file.read()

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

# Buscar la posición adecuada para insertar el botón
insertion_point = content.find('</div><!-- Fin contenido principal -->')
if insertion_point == -1:
    insertion_point = content.find('</div></div></div>')
    if insertion_point == -1:
        insertion_point = content.find('</body>')
        if insertion_point == -1:
            print("❌ No se pudo encontrar un punto para insertar el botón")
            exit(1)
        else:
            print("Insertando antes del cierre del body")
    else:
        print("Insertando antes del triple cierre de div")
else:
    print("Insertando antes del cierre del contenido principal")

# Insertar el HTML del botón
new_content = content[:insertion_point] + button_html + content[insertion_point:]

# Insertar el JavaScript antes del cierre del body
js_insertion_point = new_content.find('</body>')
if js_insertion_point != -1:
    new_content = new_content[:js_insertion_point] + button_js + new_content[js_insertion_point:]
    print("✅ JavaScript insertado correctamente")
else:
    print("❌ No se pudo encontrar el cierre del body para insertar el JavaScript")
    exit(1)

# Guardar el archivo modificado
print(f"Guardando cambios en: {template_path}")
with open(template_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print("✅ ¡Botón añadido correctamente!")
print("   Ahora puedes acceder a la página para ver el botón:")
print("   http://localhost:5000/panel_cliente/aura/google_ads/cuentas")
