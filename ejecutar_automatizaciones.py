#!/usr/bin/env python3
"""
Script para ejecutar automatizaciones desde línea de comandos
Puede ser usado por cron jobs o ejecutores de tareas
"""

import sys
import argparse
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append('.')

from clientes.aura.utils.automatizaciones_ejecutor import ejecutor

def main():
    parser = argparse.ArgumentParser(description='Ejecutor de automatizaciones')
    parser.add_argument('--id', type=str, help='ID específico de automatización a ejecutar')
    parser.add_argument('--todas', action='store_true', help='Ejecutar todas las automatizaciones pendientes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Salida detallada')
    
    args = parser.parse_args()
    
    print(f"🤖 Ejecutor de Automatizaciones - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if args.id:
        # Ejecutar automatización específica
        print(f"🎯 Ejecutando automatización ID: {args.id}")
        resultado = ejecutor.ejecutar_por_id(args.id)
        
        if resultado['success']:
            print("✅ Automatización ejecutada exitosamente")
            if args.verbose:
                print(f"📋 Resultado: {resultado.get('resultado', 'N/A')}")
        else:
            print(f"❌ Error en automatización: {resultado.get('error', 'Error desconocido')}")
            sys.exit(1)
    
    elif args.todas:
        # Ejecutar todas las automatizaciones pendientes
        print("🔄 Ejecutando todas las automatizaciones pendientes...")
        resultado = ejecutor.ejecutar_automatizaciones_pendientes()
        
        if resultado['success']:
            print(f"✅ Proceso completado:")
            print(f"   - Ejecutadas: {resultado['ejecutadas']}")
            print(f"   - Fallidas: {resultado['fallidas']}")
            
            if args.verbose and resultado['resultados']:
                print("\n📋 Detalles de ejecución:")
                for res in resultado['resultados']:
                    status = "✅" if res['success'] else "❌"
                    print(f"   {status} {res['nombre']}")
                    if not res['success']:
                        print(f"      Error: {res.get('error', 'N/A')}")
        else:
            print(f"❌ Error en el proceso: {resultado.get('error', 'Error desconocido')}")
            sys.exit(1)
    
    else:
        # Mostrar ayuda si no se especifica acción
        parser.print_help()
        print("\nEjemplos de uso:")
        print("  python ejecutar_automatizaciones.py --todas")
        print("  python ejecutar_automatizaciones.py --id abc123-def456")
        print("  python ejecutar_automatizaciones.py --todas --verbose")
    
    print("=" * 60)
    print("🏁 Proceso finalizado")

if __name__ == "__main__":
    main()
