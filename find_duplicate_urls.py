#!/usr/bin/env python3
"""
Script para encontrar y corregir URLs duplicadas en templates de Google Ads
"""

import os
import re
import glob

def find_duplicate_urls():
    """Encuentra URLs con nombre_nora duplicado en templates"""
    
    # Patrones a buscar
    patterns = [
        r'nombre_nora.*nombre_nora',  # Template variables duplicadas
        r'/panel_cliente/\{\{.*nombre_nora.*\}\}/google_ads/.*/\{\{.*nombre_nora.*\}\}/',  # URLs con doble nombre_nora
        r'fetch\(`[^`]*nombre_nora[^`]*nombre_nora[^`]*`',  # Fetch con URLs duplicadas
    ]
    
    # Directorios a revisar
    template_dirs = [
        'clientes/aura/templates/**/*.html',
        'clientes/aura/templates/*.html'
    ]
    
    problems_found = []
    
    for pattern_dir in template_dirs:
        files = glob.glob(pattern_dir, recursive=True)
        
        for file_path in files:
            if 'google_ads' in file_path.lower():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            for pattern in patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    problems_found.append({
                                        'file': file_path,
                                        'line': i,
                                        'content': line.strip(),
                                        'pattern': pattern
                                    })
                                    
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return problems_found

def main():
    print("🔍 BUSCANDO URLs DUPLICADAS EN TEMPLATES GOOGLE ADS")
    print("=" * 60)
    
    problems = find_duplicate_urls()
    
    if not problems:
        print("✅ No se encontraron problemas de URLs duplicadas")
        return
    
    print(f"❌ Se encontraron {len(problems)} problemas:")
    print()
    
    grouped_by_file = {}
    for problem in problems:
        file_path = problem['file']
        if file_path not in grouped_by_file:
            grouped_by_file[file_path] = []
        grouped_by_file[file_path].append(problem)
    
    for file_path, file_problems in grouped_by_file.items():
        print(f"📄 {file_path}")
        for problem in file_problems:
            print(f"   Línea {problem['line']}: {problem['content'][:100]}...")
        print()
    
    print("🔧 RECOMENDACIONES:")
    print("- Revisar cada archivo manualmente")
    print("- Eliminar el segundo {{ nombre_nora }} en las URLs")
    print("- Usar url_for() cuando sea posible en lugar de URLs hardcodeadas")

if __name__ == "__main__":
    main()
