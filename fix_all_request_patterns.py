#!/usr/bin/env python3
"""
Script DEFINITIVO para corregir TODAS las líneas con request.path.split en redes sociales
Captura TODAS las variaciones: con comentarios, sin comentarios, diferentes formatos
"""

import re

def fix_all_patterns_comprehensive():
    file_path = r"clientes\aura\routes\panel_cliente_redes_sociales\panel_cliente_redes_sociales.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar TODOS los patrones de request.path.split("/")[2]
    patterns_to_fix = [
        # Con comentario específico
        r'nombre_nora = request\.path\.split\("/"\)\[2\]\s*#\s*Extraer de la URL',
        # Con cualquier comentario
        r'nombre_nora = request\.path\.split\("/"\)\[2\]\s*#.*',
        # Sin comentario
        r'nombre_nora = request\.path\.split\("/"\)\[2\]\s*$',
        # Con espacios variables
        r'nombre_nora\s*=\s*request\.path\.split\("/"\)\[2\].*'
    ]
    
    replacement = 'nombre_nora = request.view_args.get("nombre_nora")'
    
    total_replacements = 0
    
    for pattern in patterns_to_fix:
        matches = re.findall(pattern, content, re.MULTILINE)
        count = len(matches)
        if count > 0:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            total_replacements += count
            print(f"✅ Patrón '{pattern[:30]}...' → {count} reemplazos")
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎯 TOTAL: {total_replacements} patrones corregidos")
    print(f"🔄 Auto-reload activado - servidor se reiniciará automáticamente")
    
    return total_replacements

if __name__ == "__main__":
    fix_all_patterns_comprehensive()
