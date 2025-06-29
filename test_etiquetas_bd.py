#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 SCRIPT DE PRUEBAS - Etiqueta "curso inteligencia artificial"
Herramienta para probar y analizar bloques de conocimiento con etiquetas específicas.
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

def conectar_bd():
    """Conectar a la base de datos"""
    try:
        # Buscar la base de datos en varios lugares posibles
        posibles_rutas = [
            'ruta_a_tu_base_de_datos.db',
            'clientes/aura/database.db',
            'database.db',
            '../database.db'
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                print(f"✅ Base de datos encontrada en: {ruta}")
                return sqlite3.connect(ruta)
        
        print("❌ No se encontró la base de datos en las rutas esperadas")
        print("📁 Rutas buscadas:")
        for ruta in posibles_rutas:
            print(f"   - {os.path.abspath(ruta)}")
        return None
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def obtener_bloques_conocimiento(conn):
    """Obtener todos los bloques de conocimiento"""
    try:
        cursor = conn.cursor()
        
        # Intentar diferentes nombres de tabla
        tablas_posibles = [
            'conocimiento',
            'knowledge_base',
            'bloques_conocimiento',
            'base_conocimiento'
        ]
        
        for tabla in tablas_posibles:
            try:
                query = f"SELECT * FROM {tabla} WHERE activo = 1 OR activo IS NULL"
                cursor.execute(query)
                resultados = cursor.fetchall()
                
                # Obtener nombres de columnas
                columnas = [description[0] for description in cursor.description]
                
                print(f"✅ Tabla encontrada: {tabla}")
                print(f"📊 Total de bloques: {len(resultados)}")
                print(f"📋 Columnas: {', '.join(columnas)}")
                
                # Convertir a lista de diccionarios
                bloques = []
                for fila in resultados:
                    bloque = dict(zip(columnas, fila))
                    bloques.append(bloque)
                
                return bloques
                
            except sqlite3.OperationalError:
                continue
        
        print("❌ No se encontró ninguna tabla de conocimiento válida")
        
        # Mostrar todas las tablas disponibles
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        print("📋 Tablas disponibles en la base de datos:")
        for tabla in tablas:
            print(f"   - {tabla[0]}")
        
        return []
        
    except Exception as e:
        print(f"❌ Error obteniendo bloques: {e}")
        return []

def analizar_etiquetas(bloques):
    """Analizar las etiquetas de los bloques"""
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE ETIQUETAS")
    print("="*60)
    
    todas_etiquetas = {}
    bloques_con_etiquetas = 0
    bloques_sin_etiquetas = 0
    
    for bloque in bloques:
        etiquetas_texto = bloque.get('etiquetas', '') or bloque.get('tags', '') or ''
        
        if etiquetas_texto and etiquetas_texto.strip():
            bloques_con_etiquetas += 1
            etiquetas_lista = [e.strip().lower() for e in etiquetas_texto.split(',') if e.strip()]
            
            for etiqueta in etiquetas_lista:
                todas_etiquetas[etiqueta] = todas_etiquetas.get(etiqueta, 0) + 1
        else:
            bloques_sin_etiquetas += 1
    
    print(f"📊 Bloques con etiquetas: {bloques_con_etiquetas}")
    print(f"📊 Bloques sin etiquetas: {bloques_sin_etiquetas}")
    print(f"📊 Etiquetas únicas: {len(todas_etiquetas)}")
    
    if todas_etiquetas:
        print("\n🏷️  ETIQUETAS MÁS FRECUENTES:")
        etiquetas_ordenadas = sorted(todas_etiquetas.items(), key=lambda x: x[1], reverse=True)
        
        for i, (etiqueta, frecuencia) in enumerate(etiquetas_ordenadas[:20]):
            destacar = any(palabra in etiqueta for palabra in ['curso', 'inteligencia', 'ia', 'artificial'])
            prefijo = "🎯" if destacar else "  "
            print(f"   {prefijo} {etiqueta}: {frecuencia} bloques")
    
    return todas_etiquetas

def buscar_por_etiqueta(bloques, etiqueta_buscada):
    """Buscar bloques que contengan una etiqueta específica"""
    print(f"\n🔍 BÚSQUEDA POR ETIQUETA: '{etiqueta_buscada}'")
    print("-" * 50)
    
    etiqueta_buscada = etiqueta_buscada.lower()
    bloques_encontrados = []
    
    for bloque in bloques:
        etiquetas_texto = bloque.get('etiquetas', '') or bloque.get('tags', '') or ''
        
        if etiquetas_texto:
            etiquetas_lista = [e.strip().lower() for e in etiquetas_texto.split(',')]
            
            # Buscar coincidencias (exacta o parcial)
            coincidencia = False
            for etiqueta in etiquetas_lista:
                if etiqueta_buscada in etiqueta or etiqueta in etiqueta_buscada:
                    coincidencia = True
                    break
            
            if coincidencia:
                bloques_encontrados.append(bloque)
                
                print(f"\n✅ BLOQUE ID: {bloque.get('id', 'N/A')}")
                print(f"   Pregunta: {bloque.get('pregunta', 'N/A')[:100]}...")
                print(f"   Etiquetas: [{', '.join(etiquetas_lista)}]")
                print(f"   Fecha: {bloque.get('fecha_creacion', 'N/A')}")
    
    print(f"\n📊 RESULTADO: {len(bloques_encontrados)} bloques encontrados")
    return bloques_encontrados

def buscar_variaciones(bloques):
    """Buscar diferentes variaciones relacionadas con curso de IA"""
    print("\n" + "="*60)
    print("🔍 BÚSQUEDA DE VARIACIONES")
    print("="*60)
    
    variaciones = [
        'curso inteligencia artificial',
        'curso ia',
        'inteligencia artificial',
        'curso',
        'ia',
        'artificial',
        'inteligencia',
        'machine learning',
        'ml',
        'deep learning'
    ]
    
    resultados = {}
    
    for variacion in variaciones:
        print(f"\n🔍 Probando: '{variacion}'")
        bloques_encontrados = buscar_por_etiqueta(bloques, variacion)
        resultados[variacion] = len(bloques_encontrados)
    
    print("\n📊 RESUMEN DE VARIACIONES:")
    print("-" * 30)
    for variacion, cantidad in resultados.items():
        print(f"   '{variacion}': {cantidad} bloques")
    
    return resultados

def exportar_resultados(bloques, etiquetas, resultados_variaciones):
    """Exportar resultados a un archivo JSON"""
    datos_exportacion = {
        'timestamp': str(os.popen('date').read().strip()) if os.name != 'nt' else 'N/A',
        'total_bloques': len(bloques),
        'estadisticas_etiquetas': {
            'total_etiquetas_unicas': len(etiquetas),
            'etiquetas_frecuentes': dict(list(sorted(etiquetas.items(), key=lambda x: x[1], reverse=True))[:10])
        },
        'resultados_variaciones': resultados_variaciones,
        'bloques_curso_ia': []
    }
    
    # Agregar bloques específicos de curso IA
    for bloque in bloques:
        etiquetas_texto = bloque.get('etiquetas', '') or ''
        if etiquetas_texto:
            etiquetas_lista = [e.strip().lower() for e in etiquetas_texto.split(',')]
            if any('curso' in e and ('ia' in e or 'inteligencia' in e) for e in etiquetas_lista):
                datos_exportacion['bloques_curso_ia'].append({
                    'id': bloque.get('id'),
                    'pregunta': bloque.get('pregunta', '')[:200],
                    'etiquetas': etiquetas_lista,
                    'fecha_creacion': bloque.get('fecha_creacion')
                })
    
    archivo_salida = 'test_etiquetas_resultado.json'
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos_exportacion, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados exportados a: {archivo_salida}")
    except Exception as e:
        print(f"❌ Error exportando resultados: {e}")

def main():
    """Función principal"""
    print("🧪 SCRIPT DE PRUEBAS - ETIQUETA 'CURSO INTELIGENCIA ARTIFICIAL'")
    print("="*70)
    
    # Conectar a la base de datos
    conn = conectar_bd()
    if not conn:
        print("❌ No se puede continuar sin conexión a la base de datos")
        sys.exit(1)
    
    try:
        # Obtener bloques
        bloques = obtener_bloques_conocimiento(conn)
        if not bloques:
            print("❌ No se encontraron bloques de conocimiento")
            sys.exit(1)
        
        # Analizar etiquetas
        etiquetas = analizar_etiquetas(bloques)
        
        # Buscar variaciones
        resultados_variaciones = buscar_variaciones(bloques)
        
        # Búsqueda específica principal
        print("\n" + "="*60)
        print("🎯 BÚSQUEDA PRINCIPAL: 'curso inteligencia artificial'")
        print("="*60)
        bloques_principales = buscar_por_etiqueta(bloques, 'curso inteligencia artificial')
        
        # Exportar resultados
        exportar_resultados(bloques, etiquetas, resultados_variaciones)
        
        # Resumen final
        print("\n" + "="*60)
        print("📋 RESUMEN FINAL")
        print("="*60)
        print(f"📊 Total de bloques analizados: {len(bloques)}")
        print(f"🏷️  Total de etiquetas únicas: {len(etiquetas)}")
        print(f"🎯 Bloques con 'curso inteligencia artificial': {len(bloques_principales)}")
        print(f"📈 Porcentaje de precisión: {(len(bloques_principales) / len(bloques) * 100):.1f}%")
        
        print("\n💡 RECOMENDACIONES:")
        if len(bloques_principales) == 0:
            print("   ⚠️  No se encontraron bloques con la etiqueta específica")
            print("   💡 Considera agregar bloques con esta etiqueta para pruebas")
        elif len(bloques_principales) < 5:
            print("   ⚠️  Pocos bloques encontrados")
            print("   💡 Podrías agregar más contenido relacionado")
        else:
            print("   ✅ Cantidad adecuada de bloques encontrados")
        
        print("\n✅ PRUEBAS COMPLETADAS")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
