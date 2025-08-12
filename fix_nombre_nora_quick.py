#!/usr/bin/env python3
"""
Script para corregir todas las referencias a request.view_args.get("nombre_nora")
"""

import re

# Leer el archivo
file_path = "clientes/aura/routes/panel_cliente_redes_sociales/panel_cliente_redes_sociales.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar todas las ocurrencias problemáticas
# Patrón: nombre_nora = request.view_args.get("nombre_nora")
pattern = r'nombre_nora = request\.view_args\.get\("nombre_nora"\)'
replacement = 'nombre_nora = get_nombre_nora()'

new_content = re.sub(pattern, replacement, content)

# Escribir el archivo corregido
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Corregidas todas las referencias a nombre_nora")
print(f"📁 Archivo: {file_path}")
