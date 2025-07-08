#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 INSPECTOR DE BASE DE DATOS - Conocimiento y Etiquetas
Herramienta para inspeccionar la estructura de la base de datos y encontrar datos.
"""

import sqlite3
import os
import json
from pathlib import Path

def encontrar_base_datos():
    """Encontrar la base de datos en el proyecto"""
    print("🔍 Buscando base de datos...")
    
    rutas_posibles = [
        'ruta_a_tu_base_de_datos.db',
        'clientes/aura/database.db',
        'database.db',
        'app.db',
        'conocimiento.db',
        'aura.db'
    ]
    
    # También buscar en subdirectorios
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db'):
                ruta_completa = os.path.join(root, file)
                rutas_posibles.append(ruta_completa)
    
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            tamaño = os.path.getsize(ruta)
            print(f"✅ Encontrada: {ruta} ({tamaño} bytes)")
            return ruta
    
    print("❌ No se encontró ninguna base de datos")
    return None

def inspeccionar_estructura(db_path):
    """Inspeccionar la estructura completa de la base de datos"""
    print(f"\n📊 INSPECCIONANDO ESTRUCTURA DE: {db_path}")
    print("="*60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        
        print(f"📋 TABLAS ENCONTRADAS ({len(tablas)}):")
        for tabla in tablas:
            print(f"   - {tabla[0]}")
        
        # Inspeccionar cada tabla que pueda contener conocimiento
        tablas_conocimiento = [
            'conocimiento', 'knowledge_base', 'bloques_conocimiento', 
            'base_conocimiento', 'nora_knowledge', 'training_data'
        ]
        
        for tabla_nombre in tablas_conocimiento:
            if (tabla_nombre,) in tablas:
                inspeccionar_tabla_conocimiento(cursor, tabla_nombre)
        
        # Si no encontramos tablas obvias, inspeccionar todas
        if not any((tabla,) in tablas for tabla in tablas_conocimiento):
            print("\n⚠️  No se encontraron tablas obvias de conocimiento")
            print("🔍 Inspeccionando todas las tablas...")
            
            for tabla in tablas:
                tabla_nombre = tabla[0]
                if not tabla_nombre.startswith('sqlite_'):
                    inspeccionar_tabla_generica(cursor, tabla_nombre)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspeccionando base de datos: {e}")

def inspeccionar_tabla_conocimiento(cursor, tabla_nombre):
    """Inspeccionar una tabla específica de conocimiento"""
    print(f"\n🎯 TABLA: {tabla_nombre}")
    print("-" * 40)
    
    try:
        # Obtener estructura de la tabla
        cursor.execute(f"PRAGMA table_info({tabla_nombre})")
        columnas = cursor.fetchall()
        
        print("📋 ESTRUCTURA:")
        for columna in columnas:
            nombre = columna[1]
            tipo = columna[2]
            no_null = "NOT NULL" if columna[3] else "NULL"
            print(f"   - {nombre}: {tipo} ({no_null})")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre}")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total}")
        
        if total > 0:
            # Obtener algunos ejemplos
            cursor.execute(f"SELECT * FROM {tabla_nombre} LIMIT 3")
            ejemplos = cursor.fetchall()
            
            print("\n📄 EJEMPLOS DE DATOS:")
            nombres_columnas = [col[1] for col in columnas]
            
            for i, ejemplo in enumerate(ejemplos, 1):
                print(f"\n   REGISTRO {i}:")
                for j, valor in enumerate(ejemplo):
                    nombre_col = nombres_columnas[j]
                    valor_str = str(valor)[:100] + "..." if len(str(valor)) > 100 else str(valor)
                    print(f"      {nombre_col}: {valor_str}")
            
            # Buscar columnas que puedan contener etiquetas
            columnas_etiquetas = [col[1] for col in columnas if 'etiqueta' in col[1].lower() or 'tag' in col[1].lower()]
            
            if columnas_etiquetas:
                print(f"\n🏷️  COLUMNAS DE ETIQUETAS ENCONTRADAS: {columnas_etiquetas}")
                
                for col_etiqueta in columnas_etiquetas:
                    cursor.execute(f"SELECT DISTINCT {col_etiqueta} FROM {tabla_nombre} WHERE {col_etiqueta} IS NOT NULL AND {col_etiqueta} != ''")
                    etiquetas_ejemplos = cursor.fetchall()
                    
                    print(f"\n   ETIQUETAS EN {col_etiqueta} ({len(etiquetas_ejemplos)} únicas):")
                    for etiqueta in etiquetas_ejemplos[:10]:  # Solo primeras 10
                        print(f"      - {etiqueta[0]}")
                    
                    if len(etiquetas_ejemplos) > 10:
                        print(f"      ... y {len(etiquetas_ejemplos) - 10} más")
                    
                    # Buscar específicamente etiquetas de curso/IA
                    cursor.execute(f"""
                        SELECT {col_etiqueta}, COUNT(*) 
                        FROM {tabla_nombre} 
                        WHERE {col_etiqueta} LIKE '%curso%' 
                           OR {col_etiqueta} LIKE '%inteligencia%' 
                           OR {col_etiqueta} LIKE '%ia%'
                           OR {col_etiqueta} LIKE '%artificial%'
                        GROUP BY {col_etiqueta}
                    """)
                    etiquetas_ia = cursor.fetchall()
                    
                    if etiquetas_ia:
                        print(f"\n   🎯 ETIQUETAS RELACIONADAS CON IA/CURSO:")
                        for etiqueta, count in etiquetas_ia:
                            print(f"      - '{etiqueta}': {count} registros")
            
            # Buscar en todas las columnas de texto etiquetas relacionadas
            columnas_texto = [col[1] for col in columnas if col[2].upper() in ['TEXT', 'VARCHAR']]
            
            print(f"\n🔍 BUSCANDO 'curso' E 'inteligencia' EN TODAS LAS COLUMNAS DE TEXTO...")
            for col in columnas_texto:
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {tabla_nombre} 
                        WHERE {col} LIKE '%curso%' OR {col} LIKE '%inteligencia%' OR {col} LIKE '%ia%'
                    """)
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"   - {col}: {count} registros contienen términos relacionados")
                        
                        # Mostrar algunos ejemplos
                        cursor.execute(f"""
                            SELECT {col} FROM {tabla_nombre} 
                            WHERE {col} LIKE '%curso%' OR {col} LIKE '%inteligencia%' OR {col} LIKE '%ia%'
                            LIMIT 3
                        """)
                        ejemplos_texto = cursor.fetchall()
                        for ejemplo in ejemplos_texto:
                            texto = str(ejemplo[0])[:150] + "..." if len(str(ejemplo[0])) > 150 else str(ejemplo[0])
                            print(f"      Ejemplo: {texto}")
                except:
                    pass
    
    except Exception as e:
        print(f"❌ Error inspeccionando tabla {tabla_nombre}: {e}")

def inspeccionar_tabla_generica(cursor, tabla_nombre):
    """Inspeccionar una tabla genérica para ver si contiene datos relevantes"""
    try:
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre}")
        total = cursor.fetchone()[0]
        
        if total > 0:
            # Obtener estructura
            cursor.execute(f"PRAGMA table_info({tabla_nombre})")
            columnas = cursor.fetchall()
            
            # Buscar columnas que puedan ser relevantes
            columnas_relevantes = []
            for col in columnas:
                nombre = col[1].lower()
                if any(palabra in nombre for palabra in ['pregunta', 'respuesta', 'question', 'answer', 'content', 'texto', 'etiqueta', 'tag']):
                    columnas_relevantes.append(col[1])
            
            if columnas_relevantes:
                print(f"\n🔍 TABLA POTENCIALMENTE RELEVANTE: {tabla_nombre}")
                print(f"   📊 Registros: {total}")
                print(f"   📋 Columnas relevantes: {columnas_relevantes}")
                
                # Buscar contenido relacionado con curso/IA
                for col in columnas_relevantes:
                    try:
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {tabla_nombre} 
                            WHERE {col} LIKE '%curso%' OR {col} LIKE '%inteligencia%' OR {col} LIKE '%ia%'
                        """)
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"   🎯 {col}: {count} registros con términos IA/curso")
                    except:
                        pass
    
    except Exception as e:
        print(f"⚠️  Error inspeccionando tabla {tabla_nombre}: {e}")

def generar_reporte_completo(db_path):
    """Generar un reporte completo de la base de datos"""
    print(f"\n📄 GENERANDO REPORTE COMPLETO...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        reporte = {
            'base_datos': db_path,
            'tamaño_archivo': os.path.getsize(db_path),
            'tablas': {},
            'resumen_conocimiento': {
                'total_registros': 0,
                'etiquetas_encontradas': [],
                'terminos_ia_curso': 0
            }
        }
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        
        for tabla in tablas:
            tabla_nombre = tabla[0]
            
            try:
                # Información básica de la tabla
                cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre}")
                total_registros = cursor.fetchone()[0]
                
                cursor.execute(f"PRAGMA table_info({tabla_nombre})")
                columnas = cursor.fetchall()
                
                reporte['tablas'][tabla_nombre] = {
                    'registros': total_registros,
                    'columnas': [col[1] for col in columnas],
                    'tipos_columnas': {col[1]: col[2] for col in columnas}
                }
                
                # Si parece una tabla de conocimiento
                columnas_nombres = [col[1].lower() for col in columnas]
                es_conocimiento = any(palabra in ' '.join(columnas_nombres) 
                                    for palabra in ['pregunta', 'respuesta', 'question', 'answer', 'etiqueta', 'tag'])
                
                if es_conocimiento:
                    reporte['resumen_conocimiento']['total_registros'] += total_registros
                    
                    # Buscar etiquetas
                    for col in columnas:
                        if 'etiqueta' in col[1].lower() or 'tag' in col[1].lower():
                            cursor.execute(f"SELECT DISTINCT {col[1]} FROM {tabla_nombre} WHERE {col[1]} IS NOT NULL")
                            etiquetas = [e[0] for e in cursor.fetchall() if e[0]]
                            reporte['resumen_conocimiento']['etiquetas_encontradas'].extend(etiquetas)
                    
                    # Contar términos IA/curso
                    for col in columnas:
                        if col[2].upper() in ['TEXT', 'VARCHAR']:
                            try:
                                cursor.execute(f"""
                                    SELECT COUNT(*) FROM {tabla_nombre} 
                                    WHERE {col[1]} LIKE '%curso%' OR {col[1]} LIKE '%inteligencia%' OR {col[1]} LIKE '%ia%'
                                """)
                                count = cursor.fetchone()[0]
                                reporte['resumen_conocimiento']['terminos_ia_curso'] += count
                            except:
                                pass
            
            except Exception as e:
                reporte['tablas'][tabla_nombre] = {'error': str(e)}
        
        # Guardar reporte
        archivo_reporte = 'reporte_bd_conocimiento.json'
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte guardado en: {archivo_reporte}")
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN DEL REPORTE:")
        print(f"   📁 Base de datos: {db_path}")
        print(f"   📊 Tablas: {len(reporte['tablas'])}")
        print(f"   📋 Registros de conocimiento: {reporte['resumen_conocimiento']['total_registros']}")
        print(f"   🏷️  Etiquetas únicas: {len(set(reporte['resumen_conocimiento']['etiquetas_encontradas']))}")
        print(f"   🎯 Registros con términos IA/curso: {reporte['resumen_conocimiento']['terminos_ia_curso']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")

def main():
    """Función principal"""
    print("🔍 INSPECTOR DE BASE DE DATOS - CONOCIMIENTO Y ETIQUETAS")
    print("="*65)
    
    # Encontrar base de datos
    db_path = encontrar_base_datos()
    if not db_path:
        print("❌ No se puede continuar sin base de datos")
        return
    
    # Inspeccionar estructura
    inspeccionar_estructura(db_path)
    
    # Generar reporte
    generar_reporte_completo(db_path)
    
    print("\n✅ INSPECCIÓN COMPLETADA")
    print("💡 Revisa el archivo 'reporte_bd_conocimiento.json' para detalles completos")

if __name__ == "__main__":
    main()
