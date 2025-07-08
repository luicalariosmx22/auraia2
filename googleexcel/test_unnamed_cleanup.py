#!/usr/bin/env python3
"""
Script para crear archivos de prueba con columnas Unnamed para verificar la limpieza
"""

import pandas as pd
import numpy as np

def create_test_file_with_unnamed():
    """Crea un archivo de prueba con columnas Unnamed"""
    
    # Datos de prueba con buenas columnas
    good_data = {
        'Campaign': ['Campaña 1', 'Campaña 2', 'Campaña 3'],
        'Ad group': ['Grupo A', 'Grupo B', 'Grupo C'], 
        'Keyword': ['palabra uno', 'palabra dos', 'palabra tres'],
        'Match type': ['Exact', 'Phrase', 'Broad'],
        'Clicks': [100, 150, 200],
        'Impressions': [1000, 1500, 2000],
        'Cost': [50.0, 75.0, 100.0]
    }
    
    # Crear DataFrame con las buenas columnas
    df = pd.DataFrame(good_data)
    
    # Agregar columnas Unnamed problemáticas
    df['Unnamed: 0'] = [np.nan, np.nan, np.nan]
    df['Unnamed: 1'] = ['', '', '']
    df['Unnamed2'] = [None, None, None]
    df['Total'] = ['TOTAL', '', '']
    df['Grand Total'] = [np.nan, np.nan, 'TOTAL GENERAL']
    df[''] = ['', '', '']  # Columna con nombre vacío
    df['Column1'] = [np.nan, np.nan, np.nan]
    
    # Agregar una fila de totales al final
    total_row = {
        'Campaign': 'Total',
        'Ad group': '',
        'Keyword': '',
        'Match type': '',
        'Clicks': 450,
        'Impressions': 4500,
        'Cost': 225.0,
        'Unnamed: 0': np.nan,
        'Unnamed: 1': '',
        'Unnamed2': None,
        'Total': 'GRAND TOTAL',
        'Grand Total': 'TOTAL GENERAL',
        '': '',
        'Column1': np.nan
    }
    
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    
    # Guardar archivo
    filename = 'test_file_with_unnamed.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Archivo de prueba creado: {filename}")
    print(f"📊 Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas")
    print(f"🔍 Columnas incluidas: {list(df.columns)}")
    print("\n🗑️ Columnas que deberían eliminarse:")
    print("  - Unnamed: 0, Unnamed: 1, Unnamed2")
    print("  - Total, Grand Total")
    print("  - Columna vacía ('')")
    print("  - Column1")
    
    return filename

def test_cleaning_function():
    """Prueba la función de limpieza"""
    filename = create_test_file_with_unnamed()
    
    print("\n" + "="*50)
    print("🧪 PROBANDO FUNCIÓN DE LIMPIEZA")
    print("="*50)
    
    # Probar con el generador de IA
    try:
        from google_ads_sql_generator import GoogleAdsExcelAnalyzer
        
        analyzer = GoogleAdsExcelAnalyzer()
        analyzer.set_table_type('palabras_clave')
        
        # Leer archivo (esto ejecutará la limpieza automáticamente)
        df = analyzer.read_excel_file(filename)
        
        print(f"\n✅ Archivo procesado exitosamente")
        print(f"📊 Dimensiones finales: {df.shape[0]} filas, {df.shape[1]} columnas")
        print(f"🔍 Columnas finales: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Error probando con IA: {e}")
    
    # Probar con el generador simple
    try:
        from simple_excel_to_sql import SimpleExcelToSQL
        
        converter = SimpleExcelToSQL()
        
        # Leer archivo manualmente para probar limpieza
        df_original = pd.read_excel(filename)
        print(f"\n📊 Antes de limpieza: {df_original.shape[1]} columnas")
        
        df_clean = converter._clean_unnamed_columns(df_original)
        print(f"📊 Después de limpieza: {df_clean.shape[1]} columnas")
        
    except Exception as e:
        print(f"❌ Error probando con generador simple: {e}")

if __name__ == "__main__":
    test_cleaning_function()
    print("\n🎯 Prueba completada. Revisa los mensajes arriba para verificar que las columnas Unnamed fueron eliminadas.")
