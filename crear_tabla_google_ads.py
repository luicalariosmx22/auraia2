#!/usr/bin/env python3
"""Script para crear la tabla google_ads_cuentas en Supabase"""

from clientes.aura.utils.supabase_client import supabase

# SQL para crear la tabla google_ads_cuentas
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS google_ads_cuentas (
    id SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    nombre_cliente TEXT NOT NULL,
    nombre_visible TEXT NOT NULL,
    empresa_id UUID REFERENCES cliente_empresas(id) ON DELETE SET NULL,
    conectada BOOLEAN DEFAULT true,
    account_status INTEGER DEFAULT 1,
    activa BOOLEAN DEFAULT true,
    moneda TEXT DEFAULT 'MXN',
    zona_horaria TEXT DEFAULT 'America/Mexico_City',
    es_test BOOLEAN DEFAULT false,
    accesible BOOLEAN DEFAULT true,
    problema TEXT,
    ads_activos INTEGER DEFAULT 0,
    anuncios_activos INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW(),
    CREATED_AT TIMESTAMP DEFAULT NOW(),
    UPDATED_AT TIMESTAMP DEFAULT NOW()
);
"""

# Índices
CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_customer_id ON google_ads_cuentas(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_nombre_visible ON google_ads_cuentas(nombre_visible);",
    "CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_empresa_id ON google_ads_cuentas(empresa_id);",
    "CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_activa ON google_ads_cuentas(activa);"
]

# Función para actualizar timestamps
CREATE_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION update_google_ads_cuentas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    NEW.UPDATED_AT = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# Trigger
CREATE_TRIGGER_SQL = """
CREATE TRIGGER trigger_update_google_ads_cuentas_updated_at
    BEFORE UPDATE ON google_ads_cuentas
    FOR EACH ROW
    EXECUTE FUNCTION update_google_ads_cuentas_updated_at();
"""

def main():
    print("📋 Creando tabla google_ads_cuentas...")
    
    try:
        # Crear tabla principal
        print("1️⃣ Creando tabla principal...")
        result = supabase.rpc('exec_sql', {'sql': CREATE_TABLE_SQL}).execute()
        print("✅ Tabla creada")
        
        # Crear índices
        print("2️⃣ Creando índices...")
        for idx_sql in CREATE_INDEXES_SQL:
            result = supabase.rpc('exec_sql', {'sql': idx_sql}).execute()
        print("✅ Índices creados")
        
        # Crear función
        print("3️⃣ Creando función de trigger...")
        result = supabase.rpc('exec_sql', {'sql': CREATE_FUNCTION_SQL}).execute()
        print("✅ Función creada")
        
        # Crear trigger
        print("4️⃣ Creando trigger...")
        result = supabase.rpc('exec_sql', {'sql': CREATE_TRIGGER_SQL}).execute()
        print("✅ Trigger creado")
        
        print("🎉 Tabla google_ads_cuentas creada exitosamente!")
        
        # Verificar que la tabla existe
        print("5️⃣ Verificando tabla...")
        test_result = supabase.table('google_ads_cuentas').select('*').limit(1).execute()
        print(f"✅ Tabla verificada: {len(test_result.data)} registros encontrados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
