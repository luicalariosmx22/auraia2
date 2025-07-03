#!/usr/bin/env python3
"""
Script de verificación para confirmar que el problema de anuncios_activos está resuelto
"""

def verificar_archivos():
    """Verifica que no haya referencias problemáticas a anuncios_activos en Google Ads"""
    import os
    import re
    
    archivos_google_ads = [
        'clientes/aura/routes/panel_cliente_google_ads.py',
        'clientes/aura/routes/panel_cliente_google_ads/vista_cuentas_publicitarias_google_ads.py'
    ]
    
    problemas_encontrados = []
    
    for archivo in archivos_google_ads:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                lineas = contenido.split('\n')
                
                for i, linea in enumerate(lineas, 1):
                    # Buscar patrones problemáticos
                    if 'anuncios_activos' in linea and '.update(' in linea:
                        problemas_encontrados.append(f"{archivo}:{i} - {linea.strip()}")
                    elif "'anuncios_activos':" in linea and 'google_ads_cuentas' in contenido:
                        # Verificar si está en un contexto de insert/update para google_ads_cuentas
                        contexto_inicio = max(0, i-10)
                        contexto_fin = min(len(lineas), i+10)
                        contexto = '\n'.join(lineas[contexto_inicio:contexto_fin])
                        
                        if '.insert(' in contexto or '.update(' in contexto:
                            if 'google_ads_cuentas' in contexto:
                                problemas_encontrados.append(f"{archivo}:{i} - {linea.strip()}")
        else:
            print(f"⚠️  Archivo no encontrado: {archivo}")
    
    return problemas_encontrados

def main():
    print("🔍 Verificando que el problema de anuncios_activos está resuelto...")
    
    problemas = verificar_archivos()
    
    if problemas:
        print("❌ Se encontraron problemas:")
        for problema in problemas:
            print(f"  - {problema}")
        return False
    else:
        print("✅ No se encontraron referencias problemáticas a 'anuncios_activos' en Google Ads")
        print("✅ El problema del error 'Could not find the anuncios_activos column' debería estar resuelto")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
