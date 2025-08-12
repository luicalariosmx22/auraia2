#!/usr/bin/env python3
"""
Script FINAL para corregir las últimas 5 líneas
"""

def fix_final_lines():
    file_path = r"clientes\aura\routes\panel_cliente_redes_sociales\panel_cliente_redes_sociales.py"
    
    # Leer archivo línea por línea
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    target_lines = [129, 150, 171, 192, 212]  # Líneas que sabemos tienen el problema
    corrections = 0
    
    for line_num in target_lines:
        if line_num <= len(lines):
            line_index = line_num - 1  # Convertir a índice (empezando en 0)
            if 'request.path.split("/")[2]' in lines[line_index]:
                lines[line_index] = '    nombre_nora = request.view_args.get("nombre_nora")\n'
                corrections += 1
                print(f"✅ Línea {line_num} corregida")
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n🎯 TOTAL: {corrections} líneas finales corregidas")
    print(f"🔄 Auto-reload activado - servidor se reiniciará automáticamente")
    
    return corrections

if __name__ == "__main__":
    fix_final_lines()
