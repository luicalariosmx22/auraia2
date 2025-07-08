#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para iniciar el servidor Flask y verificar que arranca correctamente
con las correcciones realizadas.
"""

import os
import sys
from clientes.aura import create_app

def main():
    print("\n🚀 Iniciando servidor Flask...\n")
    
    try:
        # Crear la aplicación
        app = create_app()
        
        # Mostrar información sobre los blueprints registrados
        print("\n📋 Blueprints registrados:")
        for blueprint_name in app.blueprints:
            print(f"  - {blueprint_name}")
            
        # Mostrar información sobre las rutas
        print("\n📋 Rutas disponibles:")
        for rule in app.url_map.iter_rules():
            print(f"  - {rule}")
            
        # Iniciar el servidor
        print("\n🌐 Iniciando servidor en http://localhost:5000...")
        print("⚠️ Presiona Ctrl+C para detener el servidor")
        app.run(host="0.0.0.0", port=5000, debug=True)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error al iniciar el servidor Flask: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
