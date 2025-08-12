#!/usr/bin/env python3
"""
Script para arreglar el patrón incorrecto de nombre_nora en redes sociales
Siguiendo las reglas de la biblia: usar request.view_args.get("nombre_nora")
"""

import re

def fix_nombre_nora_pattern():
    """Arregla todas las instancias del patrón incorrecto"""
    
    file_path = "clientes/aura/routes/panel_cliente_redes_sociales/panel_cliente_redes_sociales.py"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón a buscar: nombre_nora = request.path.split("/")[2]  # Extraer de la URL
    old_pattern = r'nombre_nora = request\.path\.split\("/"\)\[2\]  # Extraer de la URL'
    
    # Nuevo patrón según la biblia
    new_pattern = 'nombre_nora = request.view_args.get("nombre_nora")'
    
    # Reemplazar todas las instancias
    new_content = re.sub(old_pattern, new_pattern, content)
    
    # Contar reemplazos
    count = content.count('request.path.split("/")[2]  # Extraer de la URL')
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Arregladas {count} instancias del patrón incorrecto")
    print(f"✅ Archivo actualizado siguiendo la biblia: {file_path}")

if __name__ == "__main__":
    fix_nombre_nora_pattern()
