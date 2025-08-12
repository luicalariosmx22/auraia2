#!/usr/bin/env python3
"""
Script ULTRA DIRECTO para reemplazar texto exacto
"""

def fix_direct_replacement():
    file_path = r"clientes\aura\routes\panel_cliente_redes_sociales\panel_cliente_redes_sociales.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazo directo y simple
    old_text = 'nombre_nora = request.path.split("/")[2]  # Extraer de la URL'
    new_text = 'nombre_nora = request.view_args.get("nombre_nora")'
    
    # Contar ocurrencias antes
    before_count = content.count(old_text)
    
    # Reemplazar
    new_content = content.replace(old_text, new_text)
    
    # Contar ocurrencias después
    after_count = new_content.count(old_text)
    
    # Escribir archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    replaced = before_count - after_count
    print(f"✅ {replaced} líneas reemplazadas directamente")
    print(f"📊 Antes: {before_count} | Después: {after_count}")
    print(f"🔄 Auto-reload activado - servidor se reiniciará automáticamente")
    
    return replaced

if __name__ == "__main__":
    fix_direct_replacement()
