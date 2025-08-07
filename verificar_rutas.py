#!/usr/bin/env python3
"""Verificar rutas de automatización registradas"""

from clientes.aura import create_app

def main():
    app, socketio = create_app()
    print('=== Rutas de automatización encontradas ===')
    
    rutas_automatizacion = []
    for rule in app.url_map.iter_rules():
        if 'automatizacion' in rule.rule:
            metodos = list(rule.methods - {"HEAD", "OPTIONS"})
            rutas_automatizacion.append(f'  {rule.rule} {metodos}')
    
    if rutas_automatizacion:
        for ruta in rutas_automatizacion:
            print(ruta)
    else:
        print('  No se encontraron rutas de automatización')
    
    print('=== Verificación completada ===')

if __name__ == '__main__':
    main()
