#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para registrar webhooks en cuentas publicitarias de Meta Ads
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.meta_webhook_helpers import (
    registrar_webhook_en_cuenta,
    registrar_webhooks_en_cuentas_activas,
    verificar_webhook_registrado
)

def obtener_access_token():
    """Obtiene el access token desde variables de entorno"""
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN en las variables de entorno")
        print("💡 Configura tu token con:")
        print("   export META_ACCESS_TOKEN='tu_token_aqui'")
        print("   # O en Windows:")
        print("   set META_ACCESS_TOKEN=tu_token_aqui")
        return None
    
    return access_token

def menu_principal():
    """Muestra el menú principal de opciones"""
    print("\n" + "="*60)
    print("🚀 REGISTRO DE WEBHOOKS PARA META ADS")
    print("="*60)
    print("1. 📡 Registrar webhook en una cuenta específica")
    print("2. 🔄 Registrar webhooks en todas las cuentas activas")
    print("3. 🔍 Verificar webhook en una cuenta")
    print("4. 📊 Ver estado de todas las cuentas")
    print("5. ❌ Salir")
    print("="*60)

def registrar_cuenta_especifica(access_token):
    """Registra webhook en una cuenta específica"""
    print("\n🎯 REGISTRO EN CUENTA ESPECÍFICA")
    print("-" * 40)
    
    account_id = input("Ingresa el ID de la cuenta (ej: 123456789): ").strip()
    
    if not account_id:
        print("❌ ID de cuenta no puede estar vacío")
        return
    
    # Agregar prefijo 'act_' si no lo tiene
    if not account_id.startswith('act_'):
        account_id = f"act_{account_id}"
    
    print(f"\n🔗 Registrando webhook para: {account_id}")
    resultado = registrar_webhook_en_cuenta(account_id, access_token)
    
    if 'error' in resultado:
        print(f"❌ Falló el registro: {resultado['error']}")
    else:
        print(f"✅ Registro exitoso: {resultado}")

def verificar_cuenta_especifica(access_token):
    """Verifica webhook en una cuenta específica"""
    print("\n🔍 VERIFICAR WEBHOOK EN CUENTA")
    print("-" * 40)
    
    account_id = input("Ingresa el ID de la cuenta (ej: 123456789): ").strip()
    
    if not account_id:
        print("❌ ID de cuenta no puede estar vacío")
        return
    
    # Agregar prefijo 'act_' si no lo tiene
    if not account_id.startswith('act_'):
        account_id = f"act_{account_id}"
    
    print(f"\n🔍 Verificando webhook para: {account_id}")
    resultado = verificar_webhook_registrado(account_id, access_token)
    
    if resultado.get('success'):
        if resultado.get('registered'):
            print(f"✅ Webhook registrado en {account_id}")
            apps = resultado.get('subscribed_apps', [])
            if apps:
                print(f"📱 Apps suscritas: {len(apps)}")
                for i, app in enumerate(apps, 1):
                    print(f"   {i}. App ID: {app.get('id', 'N/A')}")
        else:
            print(f"❌ Webhook NO registrado en {account_id}")
    else:
        print(f"❌ Error verificando: {resultado.get('error', 'Error desconocido')}")

def mostrar_estado_cuentas(access_token):
    """Muestra el estado de webhooks en todas las cuentas"""
    print("\n📊 ESTADO DE WEBHOOKS EN TODAS LAS CUENTAS")
    print("-" * 50)
    
    # Obtener cuentas de Supabase
    from clientes.aura.utils.supabase_client import supabase
    
    try:
        # Obtener TODAS las cuentas y filtrar localmente
        resultado = supabase.table("meta_ads_cuentas") \
            .select("id_cuenta_publicitaria, nombre_cliente, estado_actual") \
            .execute()

        # Filtrar localmente: incluir NULL y todo excepto 'excluida'
        todas_cuentas = resultado.data or []
        cuentas = [
            cuenta for cuenta in todas_cuentas 
            if cuenta.get('estado_actual') != 'excluida'
        ]
        
        if not cuentas:
            print("❌ No se encontraron cuentas activas")
            return
        
        print(f"🔍 Verificando {len(cuentas)} cuentas activas...")
        print()
        
        for i, cuenta in enumerate(cuentas, 1):
            # El id_cuenta_publicitaria de la base ya contiene solo números
            account_id = cuenta['id_cuenta_publicitaria']
            nombre = cuenta.get('nombre_cliente', 'Sin nombre')
            
            print(f"{i}. {nombre} (act_{account_id})")
            
            # Verificar estado del webhook
            estado = verificar_webhook_registrado(account_id, access_token)
            
            if estado.get('success'):
                if estado.get('registered'):
                    print(f"   ✅ Webhook registrado")
                else:
                    print(f"   ❌ Webhook NO registrado")
            else:
                print(f"   ⚠️ Error: {estado.get('error', 'Error desconocido')}")
            
            print()
        
    except Exception as e:
        print(f"❌ Error obteniendo cuentas: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando sistema de registro de webhooks...")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Obtener access token
    access_token = obtener_access_token()
    if not access_token:
        return
    
    print("✅ Access token configurado")
    
    while True:
        menu_principal()
        
        try:
            opcion = input("\nSelecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                registrar_cuenta_especifica(access_token)
                
            elif opcion == '2':
                print("\n🔄 REGISTRO MASIVO EN CUENTAS ACTIVAS")
                print("-" * 45)
                confirmar = input("¿Confirmas registrar webhooks en TODAS las cuentas activas? (s/N): ")
                
                if confirmar.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                    resultados = registrar_webhooks_en_cuentas_activas(access_token)
                    
                    print(f"\n📊 RESUMEN DEL REGISTRO MASIVO:")
                    print(f"   Total cuentas procesadas: {len(resultados)}")
                    
                    exitosos = [r for r in resultados if r.get('success')]
                    fallidos = [r for r in resultados if not r.get('success')]
                    
                    print(f"   ✅ Exitosos: {len(exitosos)}")
                    print(f"   ❌ Fallidos: {len(fallidos)}")
                    
                    if fallidos:
                        print("\n❌ Cuentas con errores:")
                        for cuenta in fallidos:
                            print(f"   • {cuenta.get('account_id')}: {cuenta.get('resultado', {}).get('error', 'Error desconocido')}")
                else:
                    print("❌ Operación cancelada")
                    
            elif opcion == '3':
                verificar_cuenta_especifica(access_token)
                
            elif opcion == '4':
                mostrar_estado_cuentas(access_token)
                
            elif opcion == '5':
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Por favor selecciona 1-5.")
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
