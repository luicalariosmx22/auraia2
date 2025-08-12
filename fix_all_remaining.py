#!/usr/bin/env python3
"""
Script MASIVO para corregir todas las líneas restantes con request.path.split
"""

def fix_all_remaining_lines():
    file_path = r"clientes\aura\routes\panel_cliente_redes_sociales\panel_cliente_redes_sociales.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar y reemplazar línea por línea
    replacements = 0
    for i, line in enumerate(lines):
        if 'nombre_nora = request.path.split("/")[2]' in line:
            lines[i] = '    nombre_nora = request.view_args.get("nombre_nora")\n'
            replacements += 1
            print(f"✅ Línea {i+1}: {line.strip()} → request.view_args.get")
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n🎯 TOTAL: {replacements} líneas corregidas")
    print(f"🔄 Auto-reload activado - servidor se reiniciará automáticamente")
    
    return replacements

if __name__ == "__main__":
    fix_all_remaining_lines()
