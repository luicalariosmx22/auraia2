#!/usr/bin/env python3
"""
Script para verificar y crear las columnas faltantes en las tablas de Meta Ads
"""

from clientes.aura.utils.supabase_client import supabase

def verificar_y_crear_columnas():
    """
    Verifica las columnas existentes en las tablas de Meta Ads y sugiere las que faltan
    """
    print("🔍 Verificando estructura de tablas Meta Ads...")
    
    # Tablas y columnas esperadas
    tablas_esperadas = {
        'meta_ads_campañas': [
            'id',
            'campana_id', 
            'nombre_campana',
            'id_cuenta_publicitaria',
            'status',
            'objective',  # ← Esta columna falta
            'created_at'
        ],
        'meta_ads_conjuntos_anuncios': [
            'id',
            'conjunto_id',
            'nombre_conjunto',
            'campana_id',
            'id_cuenta_publicitaria',
            'status',
            'created_at'
        ],
        'meta_ads_anuncios_detalle': [
            'id',
            'anuncio_id',
            'nombre_anuncio',
            'conjunto_id',
            'campana_id',
            'id_cuenta_publicitaria',
            'status',
            'created_at'
        ]
    }
    
    # Verificar cada tabla
    for tabla, columnas_esperadas in tablas_esperadas.items():
        print(f"\n📊 Verificando tabla: {tabla}")
        
        try:
            # Intentar hacer una consulta pequeña para ver qué columnas existen
            resultado = supabase.table(tabla).select("*").limit(1).execute()
            print(f"✅ Tabla {tabla} existe y es accesible")
            
            # Si hay datos, mostrar las columnas que tienen
            if resultado.data:
                columnas_existentes = list(resultado.data[0].keys())
                print(f"   Columnas existentes: {columnas_existentes}")
                
                # Verificar columnas faltantes
                columnas_faltantes = [col for col in columnas_esperadas if col not in columnas_existentes]
                if columnas_faltantes:
                    print(f"   ❌ Columnas faltantes: {columnas_faltantes}")
                else:
                    print(f"   ✅ Todas las columnas esperadas están presentes")
            else:
                print(f"   ⚠️  Tabla {tabla} está vacía, no se pueden verificar columnas")
                
        except Exception as e:
            print(f"   ❌ Error al acceder a tabla {tabla}: {e}")
    
    print("\n" + "="*60)
    print("SOLUCIONES SUGERIDAS:")
    print("="*60)
    
    print("\n1. Para agregar la columna 'objective' a meta_ads_campañas:")
    print("   ALTER TABLE meta_ads_campañas ADD COLUMN objective TEXT;")
    
    print("\n2. Script SQL completo para crear todas las tablas con las columnas correctas:")
    print_create_tables_sql()

def print_create_tables_sql():
    """
    Imprime el SQL para crear las tablas con todas las columnas necesarias
    """
    sql_statements = [
        """
-- Tabla meta_ads_campañas
CREATE TABLE IF NOT EXISTS meta_ads_campañas (
    id BIGSERIAL PRIMARY KEY,
    campana_id TEXT NOT NULL,
    nombre_campana TEXT,
    id_cuenta_publicitaria TEXT NOT NULL,
    status TEXT,
    objective TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(campana_id, id_cuenta_publicitaria)
);""",
        """
-- Tabla meta_ads_conjuntos_anuncios  
CREATE TABLE IF NOT EXISTS meta_ads_conjuntos_anuncios (
    id BIGSERIAL PRIMARY KEY,
    conjunto_id TEXT NOT NULL,
    nombre_conjunto TEXT,
    campana_id TEXT NOT NULL,
    id_cuenta_publicitaria TEXT NOT NULL,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(conjunto_id, id_cuenta_publicitaria)
);""",
        """
-- Tabla meta_ads_anuncios_detalle
CREATE TABLE IF NOT EXISTS meta_ads_anuncios_detalle (
    id BIGSERIAL PRIMARY KEY,
    anuncio_id TEXT NOT NULL,
    nombre_anuncio TEXT,
    conjunto_id TEXT NOT NULL,
    campana_id TEXT NOT NULL,
    id_cuenta_publicitaria TEXT NOT NULL,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(anuncio_id, id_cuenta_publicitaria)
);"""
    ]
    
    for sql in sql_statements:
        print(sql)

if __name__ == "__main__":
    verificar_y_crear_columnas()
