#!/usr/bin/env python3
"""
Script para corregir TODAS las líneas con request.path.split en redes sociales
Siguiendo el patrón de la biblia: request.view_args.get("nombre_nora")
"""

import re

def fix_all_patterns():
    file_path = r"clientes\aura\routes\panel_cliente_redes_sociales\panel_cliente_redes_sociales.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar: nombre_nora = request.path.split("/")[2]  # Extraer de la URL
    old_pattern = r'nombre_nora = request\.path\.split\("/"\)\[2\]\s*#.*'
    new_pattern = 'nombre_nora = request.view_args.get("nombre_nora")'
    
    # Reemplazar TODAS las ocurrencias
    new_content = re.sub(old_pattern, new_pattern, content)
    
    # Contar reemplazos
    count = len(re.findall(old_pattern, content))
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {count} patrones corregidos siguiendo la biblia oficial")
    print(f"🔄 Auto-reload activado - servidor se reiniciará automáticamente")
    
    return count

if __name__ == "__main__":
    fix_all_patterns()
