#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para visualizar las métricas de Google Ads por cuenta y palabra clave.
Crea gráficas para mostrar la distribución y relaciones de métricas numéricas.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from utils.supabase_client import get_supabase_client
from datetime import datetime

def generar_reporte_visual():
    """Genera gráficas para visualizar las métricas de Google Ads"""
    try:
        print("📊 Generando visualizaciones para métricas de Google Ads...")
        
        # Obtener cliente de Supabase
        supabase = get_supabase_client()
        
        # Consultar datos de keywords con métricas
        response = supabase.table('google_ads_palabras_clave').select(
            'id, palabra_clave, campaña, nombre_cuenta, customer_id, impresiones_num, clics_num, '
            'ctr_num, costo_num, conversiones_num, conversion_rate, cpc_promedio_num'
        ).gte('impresiones_num', 0).execute()
        
        if not response.data:
            print("❌ No se encontraron datos para visualizar")
            return
            
        # Crear directorio para guardar gráficas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"google_ads_graficas_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"📂 Guardando gráficas en: {output_dir}")
        
        # Filtrar datos con valores mayores a 0 para visualizaciones significativas
        datos = response.data
        print(f"✅ Obtenidos {len(datos)} registros para visualizar")
        
        # Agrupar por cuenta
        cuentas = {}
        for record in datos:
            nombre_cuenta = record.get('nombre_cuenta')
            if not nombre_cuenta:
                continue
                
            if nombre_cuenta not in cuentas:
                cuentas[nombre_cuenta] = {
                    'customer_id': record.get('customer_id', 'N/A'),
                    'keywords': [],
                    'impresiones': [],
                    'clics': [],
                    'ctr': [],
                    'costo': [],
                    'conversiones': [],
                    'conversion_rate': [],
                    'cpc': []
                }
                
            # Añadir datos a la cuenta correspondiente
            if record.get('impresiones_num', 0) > 0:
                cuentas[nombre_cuenta]['keywords'].append(record.get('palabra_clave'))
                cuentas[nombre_cuenta]['impresiones'].append(record.get('impresiones_num', 0))
                cuentas[nombre_cuenta]['clics'].append(record.get('clics_num', 0))
                cuentas[nombre_cuenta]['ctr'].append(record.get('ctr_num', 0))
                cuentas[nombre_cuenta]['costo'].append(record.get('costo_num', 0))
                cuentas[nombre_cuenta]['conversiones'].append(record.get('conversiones_num', 0))
                cuentas[nombre_cuenta]['conversion_rate'].append(record.get('conversion_rate', 0))
                cuentas[nombre_cuenta]['cpc'].append(record.get('cpc_promedio_num', 0))
        
        # 1. Generar gráfica de barras para impresiones por cuenta
        print("\n1️⃣ Generando gráfica de impresiones totales por cuenta...")
        plt.figure(figsize=(10, 6))
        
        nombres_cuentas = list(cuentas.keys())
        impresiones_por_cuenta = [sum(cuentas[cuenta]['impresiones']) for cuenta in nombres_cuentas]
        
        bars = plt.bar(nombres_cuentas, impresiones_por_cuenta, color='skyblue')
        plt.title('Impresiones Totales por Cuenta', fontsize=15)
        plt.xlabel('Cuenta', fontsize=12)
        plt.ylabel('Impresiones', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir valores en las barras
        for bar, value in zip(bars, impresiones_por_cuenta):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
                    str(int(value)), ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/impresiones_por_cuenta.png", dpi=300)
        plt.close()
        
        # 2. Generar gráfica para CTR promedio por cuenta
        print("2️⃣ Generando gráfica de CTR promedio por cuenta...")
        plt.figure(figsize=(10, 6))
        
        ctr_promedio_por_cuenta = []
        for cuenta in nombres_cuentas:
            if cuentas[cuenta]['impresiones'] and sum(cuentas[cuenta]['impresiones']) > 0:
                ctr = (sum(cuentas[cuenta]['clics']) / sum(cuentas[cuenta]['impresiones'])) * 100
                ctr_promedio_por_cuenta.append(ctr)
            else:
                ctr_promedio_por_cuenta.append(0)
        
        bars = plt.bar(nombres_cuentas, ctr_promedio_por_cuenta, color='lightgreen')
        plt.title('CTR Promedio por Cuenta', fontsize=15)
        plt.xlabel('Cuenta', fontsize=12)
        plt.ylabel('CTR (%)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir valores en las barras
        for bar, value in zip(bars, ctr_promedio_por_cuenta):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f"{value:.2f}%", ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/ctr_promedio_por_cuenta.png", dpi=300)
        plt.close()
        
        # 3. Para cada cuenta con datos, crear gráficas específicas
        for cuenta in cuentas:
            if not cuentas[cuenta]['impresiones']:
                continue  # Saltamos cuentas sin datos
                
            print(f"\n🔍 Generando gráficas detalladas para cuenta: {cuenta}")
            
            # 3.1 Top 10 keywords por impresiones
            if len(cuentas[cuenta]['impresiones']) > 0:
                plt.figure(figsize=(12, 8))
                
                # Combinar keywords e impresiones y ordenar
                keywords_impresiones = list(zip(cuentas[cuenta]['keywords'], cuentas[cuenta]['impresiones']))
                keywords_impresiones.sort(key=lambda x: x[1], reverse=True)
                
                # Tomar los top 10 o menos si no hay tantos
                top_n = min(10, len(keywords_impresiones))
                top_keywords = [item[0] for item in keywords_impresiones[:top_n]]
                top_impresiones = [item[1] for item in keywords_impresiones[:top_n]]
                
                # Crear gráfica horizontal para keywords (más legible)
                bars = plt.barh(top_keywords, top_impresiones, color='lightblue')
                plt.title(f'Top {top_n} Keywords por Impresiones - {cuenta}', fontsize=15)
                plt.xlabel('Impresiones', fontsize=12)
                plt.gca().invert_yaxis()  # Para ordenar de mayor a menor
                plt.grid(axis='x', linestyle='--', alpha=0.7)
                
                # Añadir valores en las barras
                for bar, value in zip(bars, top_impresiones):
                    plt.text(value + (max(top_impresiones) * 0.01), bar.get_y() + bar.get_height()/2, 
                            str(int(value)), ha='left', va='center', fontsize=10)
                
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{cuenta}_top_keywords_impresiones.png", dpi=300)
                plt.close()
            
            # 3.2 Relación CTR vs. Impresiones (scatter plot)
            if len(cuentas[cuenta]['ctr']) > 0 and len(cuentas[cuenta]['impresiones']) > 0:
                plt.figure(figsize=(10, 8))
                
                # Filtrar solo elementos con impresiones > 0 y ctr > 0
                valid_indices = [i for i in range(len(cuentas[cuenta]['impresiones'])) 
                                if cuentas[cuenta]['impresiones'][i] > 0 and cuentas[cuenta]['ctr'][i] > 0]
                
                if valid_indices:
                    x = [cuentas[cuenta]['impresiones'][i] for i in valid_indices]
                    y = [cuentas[cuenta]['ctr'][i] for i in valid_indices]
                    labels = [cuentas[cuenta]['keywords'][i] for i in valid_indices]
                    
                    plt.scatter(x, y, alpha=0.7, s=50, c='blue')
                    plt.title(f'CTR vs. Impresiones - {cuenta}', fontsize=15)
                    plt.xlabel('Impresiones', fontsize=12)
                    plt.ylabel('CTR (%)', fontsize=12)
                    plt.xscale('log')  # Escala logarítmica para impresiones
                    plt.grid(True, alpha=0.3)
                    
                    # Añadir etiquetas para algunos puntos interesantes
                    max_ctr_idx = y.index(max(y)) if y else 0
                    max_imp_idx = x.index(max(x)) if x else 0
                    
                    if len(x) > 0:
                        plt.annotate(labels[max_ctr_idx], (x[max_ctr_idx], y[max_ctr_idx]), 
                                    textcoords="offset points", xytext=(0,10), ha='center')
                        plt.annotate(labels[max_imp_idx], (x[max_imp_idx], y[max_imp_idx]), 
                                    textcoords="offset points", xytext=(0,10), ha='center')
                    
                    plt.tight_layout()
                    plt.savefig(f"{output_dir}/{cuenta}_ctr_vs_impresiones.png", dpi=300)
                    plt.close()
            
            # 3.3 Conversiones vs. Clics
            if len(cuentas[cuenta]['conversiones']) > 0 and len(cuentas[cuenta]['clics']) > 0:
                plt.figure(figsize=(10, 8))
                
                # Filtrar solo elementos con clics > 0
                valid_indices = [i for i in range(len(cuentas[cuenta]['clics'])) 
                                if cuentas[cuenta]['clics'][i] > 0]
                
                if valid_indices:
                    x = [cuentas[cuenta]['clics'][i] for i in valid_indices]
                    y = [cuentas[cuenta]['conversiones'][i] for i in valid_indices]
                    labels = [cuentas[cuenta]['keywords'][i] for i in valid_indices]
                    
                    plt.scatter(x, y, alpha=0.7, s=50, c='green')
                    plt.title(f'Conversiones vs. Clics - {cuenta}', fontsize=15)
                    plt.xlabel('Clics', fontsize=12)
                    plt.ylabel('Conversiones', fontsize=12)
                    plt.grid(True, alpha=0.3)
                    
                    # Añadir etiquetas para algunos puntos interesantes
                    if y and max(y) > 0:
                        max_conv_idx = y.index(max(y))
                        plt.annotate(labels[max_conv_idx], (x[max_conv_idx], y[max_conv_idx]), 
                                    textcoords="offset points", xytext=(0,10), ha='center')
                    
                    if x and max(x) > 0:
                        max_clics_idx = x.index(max(x))
                        plt.annotate(labels[max_clics_idx], (x[max_clics_idx], y[max_clics_idx]), 
                                    textcoords="offset points", xytext=(0,10), ha='center')
                    
                    plt.tight_layout()
                    plt.savefig(f"{output_dir}/{cuenta}_conversiones_vs_clics.png", dpi=300)
                    plt.close()
        
        print(f"\n✅ Visualizaciones generadas exitosamente en {output_dir}")
        return output_dir
        
    except Exception as e:
        print(f"❌ Error generando visualizaciones: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    output_dir = generar_reporte_visual()
    if output_dir:
        print(f"\n📊 Reporte visual generado en: {output_dir}")
        print("   Revisa este directorio para ver las gráficas generadas.")
    else:
        print("\n❌ No se pudo generar el reporte visual.")
