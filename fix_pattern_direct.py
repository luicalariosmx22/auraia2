#!/usr/bin/env python3
"""
Script directo para arreglar TODAS las instancias
"""

def fix_all_patterns():
    file_path = "clientes/aura/routes/panel_cliente_redes_sociales/panel_cliente_redes_sociales.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazo simple y directo
    old_text = '    nombre_nora = request.path.split("/")[2]  # Extraer de la URL'
    new_text = '    nombre_nora = request.view_args.get("nombre_nora")'
    
    new_content = content.replace(old_text, new_text)
    
    count = content.count(old_text)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Reemplazadas {count} líneas")
    print(f"✅ Patrón corregido según la biblia")

if __name__ == "__main__":
    fix_all_patterns()
