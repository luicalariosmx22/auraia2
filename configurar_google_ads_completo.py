#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para automatizar la configuración completa de Google Ads API
"""

import os
import sys
import subprocess
import time
import argparse

def ejecutar_comando(comando, descripcion, ignorar_error=False):
    """Ejecuta un comando del sistema y muestra su salida."""
    print(f"\n🚀 {descripcion}...\n")
    print(f"$ {comando}\n")
    
    try:
        resultado = subprocess.run(
            comando, 
            shell=True, 
            check=not ignorar_error,
            text=True,
            capture_output=True
        )
        
        # Mostrar salida
        if resultado.stdout:
            print(resultado.stdout)
        
        if resultado.stderr and not ignorar_error:
            print(f"⚠️ Errores:\n{resultado.stderr}")
            
        return resultado.returncode == 0
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        if e.output:
            print(f"Salida:\n{e.output}")
        if e.stderr:
            print(f"Error:\n{e.stderr}")
        return False

def verificar_estructura_db():
    """Verifica la estructura de la base de datos."""
    return ejecutar_comando(
        "python verificar_estructura_db.py",
        "Verificando estructura de la base de datos",
        ignorar_error=True
    )

def crear_tablas():
    """Crea las tablas necesarias en Supabase."""
    print("\n📊 Creando tablas necesarias en Supabase\n")
    
    # Mostrar instrucciones
    print("""
Para crear las tablas necesarias, sigue estos pasos:

1. Accede a tu panel de control de Supabase
2. Ve a SQL Editor
3. Copia y pega el contenido del archivo scripts/crear_tabla_google_ads_config.sql
4. Ejecuta el script

Una vez completado, presiona Enter para continuar...
    """)
    
    input("Presiona Enter cuando hayas creado las tablas...")
    return True

def configurar_credenciales():
    """Configura las credenciales de Google Ads."""
    return ejecutar_comando(
        "python configurar_google_ads.py",
        "Configurando credenciales de Google Ads"
    )

def renovar_token():
    """Renueva el token de acceso."""
    return ejecutar_comando(
        "python renovar_token_google_ads.py --renew-token",
        "Renovando token de acceso"
    )

def diagnosticar_token():
    """Diagnostica el estado del token."""
    return ejecutar_comando(
        "python diagnostico_token_google_ads.py",
        "Diagnosticando estado del token"
    )

def iniciar_servidor():
    """Inicia el servidor Flask para probar la integración."""
    return ejecutar_comando(
        "python run_server.py",
        "Iniciando servidor Flask para pruebas"
    )

def ejecutar_prueba_endpoint():
    """Ejecuta una prueba del endpoint de actualización."""
    return ejecutar_comando(
        "python test_endpoint.py",
        "Probando endpoint de actualización"
    )

def flujo_completo():
    """Ejecuta el flujo completo de configuración."""
    print("\n🚀 CONFIGURACIÓN COMPLETA DE GOOGLE ADS API 🚀\n")
    print("="*80 + "\n")
    
    print("""Este script te guiará a través del proceso completo de configuración
de la integración con Google Ads API, desde la creación de tablas
hasta la prueba del endpoint de actualización.

Sigue las instrucciones en pantalla para completar cada paso.
""")
    
    pasos = [
        ("Verificar estructura de base de datos", verificar_estructura_db),
        ("Crear tablas en Supabase", crear_tablas),
        ("Configurar credenciales", configurar_credenciales),
        ("Renovar token de acceso", renovar_token),
        ("Diagnosticar token", diagnosticar_token)
    ]
    
    for nombre_paso, funcion_paso in pasos:
        print(f"\n{'='*30} PASO: {nombre_paso} {'='*30}\n")
        
        if not funcion_paso():
            print(f"\n❌ Error en el paso '{nombre_paso}'. ¿Deseas continuar de todos modos?")
            if input("Continuar? (s/n): ").lower() != 's':
                print("\n❌ Configuración cancelada por el usuario.")
                return False
        
        print(f"\n✅ Paso '{nombre_paso}' completado.")
        time.sleep(1)
    
    print("\n✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE\n")
    print("""
La integración con Google Ads API ha sido configurada correctamente.
Ahora puedes:

1. Ejecutar el servidor Flask para probar la integración:
   python run_server.py
   
2. Probar el endpoint de actualización:
   python test_endpoint.py
   
3. Acceder a la interfaz web y probar el botón "Actualizar datos últimos 7 días"
""")
    
    return True

def configuracion_rapida():
    """Ejecuta una configuración rápida sin interacciones."""
    print("\n🚀 CONFIGURACIÓN RÁPIDA DE GOOGLE ADS API 🚀\n")
    
    # Verificar estructura
    verificar_estructura_db()
    
    # Intentar configurar credenciales
    if not configurar_credenciales():
        print("❌ Error configurando credenciales.")
        return False
    
    # Renovar token
    if not renovar_token():
        print("❌ Error renovando token.")
        return False
    
    # Diagnosticar
    diagnosticar_token()
    
    print("\n✅ Configuración rápida completada.\n")
    return True

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description="Configuración de Google Ads API")
    parser.add_argument("--rapido", action="store_true", help="Ejecutar configuración rápida sin interacciones")
    parser.add_argument("--verificar", action="store_true", help="Solo verificar la estructura de la base de datos")
    parser.add_argument("--diagnosticar", action="store_true", help="Solo diagnosticar el estado del token")
    parser.add_argument("--crear-tablas", action="store_true", help="Solo crear las tablas necesarias")
    parser.add_argument("--renovar-token", action="store_true", help="Solo renovar el token de acceso")
    args = parser.parse_args()
    
    if args.verificar:
        return 0 if verificar_estructura_db() else 1
    
    if args.diagnosticar:
        return 0 if diagnosticar_token() else 1
    
    if args.crear_tablas:
        return 0 if crear_tablas() else 1
    
    if args.renovar_token:
        return 0 if renovar_token() else 1
    
    if args.rapido:
        return 0 if configuracion_rapida() else 1
    
    # Si no se especificó ninguna opción, ejecutar flujo completo
    return 0 if flujo_completo() else 1

if __name__ == "__main__":
    sys.exit(main())
