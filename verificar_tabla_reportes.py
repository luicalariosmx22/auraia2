#!/usr/bin/env python3
"""
Script para verificar y crear la estructura de la tabla meta_ads_reportes
"""

from clientes.aura.utils.supabase_client import supabase
import sys

def verificar_tabla_reportes():
    """Verifica si la tabla meta_ads_reportes existe y tiene la estructura correcta"""
    try:
        # Intentar obtener algunos registros para verificar si la tabla existe
        result = supabase.table('meta_ads_reportes').select('*').limit(1).execute()
        print("✅ Tabla meta_ads_reportes existe")
        
        if result.data:
            print("📋 Estructura actual de la tabla:")
            for key in result.data[0].keys():
                print(f"  - {key}")
        else:
            print("📋 Tabla existe pero está vacía")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")
        return False

def crear_tabla_reportes_sql():
    """Genera el SQL para crear la tabla meta_ads_reportes"""
    sql = """
    CREATE TABLE IF NOT EXISTS meta_ads_reportes (
        id SERIAL PRIMARY KEY,
        nombre_visible TEXT NOT NULL,
        id_cuenta_publicitaria TEXT NOT NULL,
        nombre_cliente TEXT NOT NULL,
        tipo_plataforma TEXT NOT NULL,
        fecha_desde DATE NOT NULL,
        fecha_hasta DATE NOT NULL,
        archivo_excel TEXT, -- Base64 encoded Excel file
        fecha_generacion TIMESTAMP DEFAULT NOW(),
        fecha_envio TIMESTAMP,
        estado TEXT DEFAULT 'pendiente', -- pendiente, completado, error
        tipo_reporte TEXT DEFAULT 'manual', -- manual, automatico, especifico
        destinatarios TEXT[], -- Array de emails para reportes automaticos
        mensaje_personalizado TEXT,
        total_anuncios INTEGER,
        gasto_total DECIMAL(10,2),
        impresiones_totales BIGINT,
        clics_totales BIGINT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Índices para mejorar el rendimiento
    CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_nombre_visible ON meta_ads_reportes(nombre_visible);
    CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_cuenta ON meta_ads_reportes(id_cuenta_publicitaria);
    CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_fecha_generacion ON meta_ads_reportes(fecha_generacion);
    CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_tipo ON meta_ads_reportes(tipo_reporte);
    """
    return sql

def main():
    print("=== VERIFICANDO ESTRUCTURA DE TABLA meta_ads_reportes ===")
    
    if not verificar_tabla_reportes():
        print("\n📝 SQL para crear la tabla:")
        print(crear_tabla_reportes_sql())
        print("\n💡 Ejecuta este SQL en tu base de datos Supabase para crear la tabla.")
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()
