#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar consultas analíticas usando los nuevos campos numéricos
en la tabla google_ads_palabras_clave.

Este script muestra el valor de tener los campos numéricos al permitir:
1. Filtrar por rangos de valores (ej: encontrar keywords con más de X impresiones)
2. Ordenar por métricas (ej: keywords más efectivas por CTR o conversiones)
3. Hacer cálculos agregados (promedios, sumas, etc.)
"""

import sys
from utils.supabase_client import get_supabase_client

def main():
    try:
        print("🔍 Realizando consultas analíticas con los campos numéricos...")
        
        # Obtener cliente de Supabase
        supabase = get_supabase_client()
        
        # 1. Palabras clave con más impresiones
        print("\n1️⃣ TOP 10 palabras clave con más impresiones:")
        response = supabase.table('google_ads_palabras_clave').select('id, palabra_clave, campaña, nombre_cuenta, impresiones_num, clics_num, ctr_num').order('impresiones_num', desc=True).limit(10).execute()
        
        if response.data:
            for i, record in enumerate(response.data):
                print(f"  {i+1}. {record['palabra_clave']} ({record['nombre_cuenta']}): {record['impresiones_num']} impresiones, {record['clics_num']} clics, CTR: {record['ctr_num']}%")
        else:
            print("  No se encontraron registros")
        
        # 2. Palabras clave con mejor CTR (con al menos 10 impresiones)
        print("\n2️⃣ TOP 10 palabras clave con mejor CTR (mín. 10 impresiones):")
        response = supabase.table('google_ads_palabras_clave').select('id, palabra_clave, campaña, nombre_cuenta, impresiones_num, clics_num, ctr_num').gte('impresiones_num', 10).order('ctr_num', desc=True).limit(10).execute()
        
        if response.data:
            for i, record in enumerate(response.data):
                print(f"  {i+1}. {record['palabra_clave']} ({record['nombre_cuenta']}): CTR {record['ctr_num']}%, {record['clics_num']}/{record['impresiones_num']}")
        else:
            print("  No se encontraron registros")
            
        # 3. Palabras clave con más conversiones
        print("\n3️⃣ TOP 10 palabras clave con más conversiones:")
        response = supabase.table('google_ads_palabras_clave').select('id, palabra_clave, campaña, nombre_cuenta, conversiones_num, clics_num, conversion_rate').order('conversiones_num', desc=True).limit(10).execute()
        
        if response.data:
            for i, record in enumerate(response.data):
                print(f"  {i+1}. {record['palabra_clave']} ({record['nombre_cuenta']}): {record['conversiones_num']} conversiones, Rate: {record['conversion_rate']}%")
        else:
            print("  No se encontraron registros")
            
        # 4. Palabras clave con mejor tasa de conversión (con al menos 1 clic)
        print("\n4️⃣ TOP 10 palabras clave con mejor tasa de conversión (mín. 1 clic):")
        response = supabase.table('google_ads_palabras_clave').select('id, palabra_clave, campaña, nombre_cuenta, conversiones_num, clics_num, conversion_rate').gte('clics_num', 1).order('conversion_rate', desc=True).limit(10).execute()
        
        if response.data:
            for i, record in enumerate(response.data):
                print(f"  {i+1}. {record['palabra_clave']} ({record['nombre_cuenta']}): {record['conversion_rate']}% ({record['conversiones_num']}/{record['clics_num']})")
        else:
            print("  No se encontraron registros")
            
        # 5. Palabras clave más costosas
        print("\n5️⃣ TOP 10 palabras clave más costosas:")
        response = supabase.table('google_ads_palabras_clave').select('id, palabra_clave, campaña, nombre_cuenta, costo_num, clics_num, conversiones_num').order('costo_num', desc=True).limit(10).execute()
        
        if response.data:
            for i, record in enumerate(response.data):
                print(f"  {i+1}. {record['palabra_clave']} ({record['nombre_cuenta']}): ${record['costo_num']} MXN, {record['clics_num']} clics, {record['conversiones_num']} conv.")
        else:
            print("  No se encontraron registros")
            
        # 6. Palabras clave con CPC más alto
        print("\n6️⃣ TOP 10 palabras clave con CPC más alto (mín. 1 clic):")
        response = supabase.table('google_ads_palabras_clave').select('id, palabra_clave, campaña, nombre_cuenta, cpc_promedio_num, clics_num').gte('clics_num', 1).order('cpc_promedio_num', desc=True).limit(10).execute()
        
        if response.data:
            for i, record in enumerate(response.data):
                print(f"  {i+1}. {record['palabra_clave']} ({record['nombre_cuenta']}): ${record['cpc_promedio_num']} MXN por clic, {record['clics_num']} clics")
        else:
            print("  No se encontraron registros")
            
        # 7. Análisis por cuenta - Métricas agregadas
        print("\n7️⃣ Métricas agregadas por cuenta:")
        # Esto requeriría SQL nativo, lo simulamos haciendo búsquedas y agrupando por cuenta
        response = supabase.table('google_ads_palabras_clave').select('nombre_cuenta, customer_id, impresiones_num, clics_num, conversiones_num, costo_num').execute()
        
        if response.data:
            # Agregar métricas por cuenta
            cuentas = {}
            for record in response.data:
                nombre_cuenta = record['nombre_cuenta']
                if nombre_cuenta not in cuentas:
                    cuentas[nombre_cuenta] = {
                        'customer_id': record['customer_id'],
                        'impresiones': 0,
                        'clics': 0,
                        'conversiones': 0,
                        'costo': 0,
                        'keywords': 0
                    }
                
                cuentas[nombre_cuenta]['impresiones'] += record['impresiones_num'] or 0
                cuentas[nombre_cuenta]['clics'] += record['clics_num'] or 0
                cuentas[nombre_cuenta]['conversiones'] += record['conversiones_num'] or 0
                cuentas[nombre_cuenta]['costo'] += record['costo_num'] or 0
                cuentas[nombre_cuenta]['keywords'] += 1
            
            # Mostrar resultados por cuenta
            for nombre_cuenta, metricas in cuentas.items():
                ctr = 0
                if metricas['impresiones'] > 0:
                    ctr = (metricas['clics'] / metricas['impresiones']) * 100
                
                conversion_rate = 0
                if metricas['clics'] > 0:
                    conversion_rate = (metricas['conversiones'] / metricas['clics']) * 100
                
                print(f"\n  📊 {nombre_cuenta} (ID: {metricas['customer_id']}):")
                print(f"    • Keywords: {metricas['keywords']}")
                print(f"    • Impresiones totales: {metricas['impresiones']}")
                print(f"    • Clics totales: {metricas['clics']}")
                print(f"    • CTR promedio: {ctr:.2f}%")
                print(f"    • Conversiones totales: {metricas['conversiones']}")
                print(f"    • Tasa de conversión: {conversion_rate:.2f}%")
                print(f"    • Costo total: ${metricas['costo']:.2f} MXN")
                
                if metricas['conversiones'] > 0:
                    costo_por_conversion = metricas['costo'] / metricas['conversiones']
                    print(f"    • Costo por conversión: ${costo_por_conversion:.2f} MXN")
                
        else:
            print("  No se encontraron registros")
        
    except Exception as e:
        print(f"❌ Error realizando consultas analíticas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
