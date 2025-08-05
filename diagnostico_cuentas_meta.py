#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar las cuentas en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase

def verificar_cuentas_bd():
    """Verifica las cuentas en la base de datos"""
    print("🔍 VERIFICANDO CUENTAS EN BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Obtener TODAS las cuentas
        resultado = supabase.table("meta_ads_cuentas") \
            .select("id, id_cuenta_publicitaria, nombre_cliente, estado_actual, conectada") \
            .execute()

        cuentas = resultado.data or []
        
        if not cuentas:
            print("❌ No se encontraron cuentas en la base de datos")
            print("💡 Asegúrate de que:")
            print("   1. La tabla 'meta_ads_cuentas' existe")
            print("   2. Hay datos en la tabla")
            print("   3. Las credenciales de Supabase son correctas")
            return
        
        print(f"📊 Total de cuentas encontradas: {len(cuentas)}")
        print()
        
        # Contar por estado
        estados = {}
        for cuenta in cuentas:
            estado = cuenta.get('estado_actual') or 'NULL'
            estados[estado] = estados.get(estado, 0) + 1
        
        print("📈 RESUMEN POR ESTADO:")
        for estado, cantidad in estados.items():
            print(f"   {estado}: {cantidad} cuentas")
        
        print("\n📋 DETALLE DE CUENTAS:")
        print("-" * 80)
        
        for i, cuenta in enumerate(cuentas, 1):
            id_cuenta = cuenta.get('id_cuenta_publicitaria', 'N/A')
            nombre = cuenta.get('nombre_cliente', 'Sin nombre')
            estado = cuenta.get('estado_actual') or 'NULL'
            conectada = cuenta.get('conectada', False)
            
            estado_emoji = {
                'NULL': '⚪',
                'activa': '✅',
                'excluida': '❌',
                'pausada': '⏸️'
            }.get(estado, '❓')
            
            conectada_emoji = '🔗' if conectada else '🔌'
            
            print(f"{i:2d}. {estado_emoji} act_{id_cuenta} - {nombre}")
            print(f"     Estado: {estado} | Conectada: {conectada} {conectada_emoji}")
            print()
        
        # Mostrar cuáles se usarían para webhooks
        cuentas_activas = [
            cuenta for cuenta in cuentas 
            if cuenta.get('estado_actual') != 'excluida'
        ]
        
        print("🎯 CUENTAS QUE SE USARÍAN PARA WEBHOOKS:")
        print(f"   Total: {len(cuentas_activas)} cuentas")
        
        if cuentas_activas:
            print("   Lista:")
            for cuenta in cuentas_activas:
                id_cuenta = cuenta.get('id_cuenta_publicitaria', 'N/A')
                nombre = cuenta.get('nombre_cliente', 'Sin nombre')
                print(f"   • act_{id_cuenta} - {nombre}")
        else:
            print("   ❌ No hay cuentas disponibles para webhooks")
            print("   💡 Esto significa que todas están marcadas como 'excluida'")
        
    except Exception as e:
        print(f"❌ Error consultando base de datos: {e}")
        print("💡 Verifica:")
        print("   1. Conexión a Supabase")
        print("   2. Permisos de la tabla")
        print("   3. Variables de entorno")

def insertar_cuenta_prueba():
    """Inserta una cuenta de prueba"""
    print("\n🧪 ¿Quieres insertar una cuenta de prueba?")
    respuesta = input("Escribe 's' para sí: ").strip().lower()
    
    if respuesta in ['s', 'si', 'sí']:
        id_cuenta = input("ID de cuenta publicitaria (solo números): ").strip()
        nombre = input("Nombre del cliente: ").strip() or "Cliente de Prueba"
        
        if id_cuenta:
            try:
                data = {
                    'id_cuenta_publicitaria': id_cuenta,
                    'nombre_cliente': nombre,
                    'estado_actual': None,  # NULL para que sea incluida
                    'conectada': False,
                    'tipo_plataforma': 'meta_ads'
                }
                
                resultado = supabase.table('meta_ads_cuentas').insert(data).execute()
                
                if resultado.data:
                    print(f"✅ Cuenta de prueba insertada: act_{id_cuenta}")
                    print("🔄 Ejecuta el script nuevamente para ver la cuenta")
                else:
                    print("❌ Error insertando cuenta de prueba")
                    
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 DIAGNÓSTICO DE CUENTAS META ADS")
    print()
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    verificar_cuentas_bd()
    insertar_cuenta_prueba()
    
    print("\n✨ Diagnóstico completado!")

if __name__ == "__main__":
    main()
