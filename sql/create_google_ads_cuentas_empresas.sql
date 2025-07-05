-- Tabla para cuentas de Google Ads (similar a meta_ads_cuentas)
-- Esta tabla almacena las cuentas de Google Ads y su vinculación con empresas
CREATE TABLE IF NOT EXISTS google_ads_cuentas (
    id SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE, -- ID de la cuenta de Google Ads (10 dígitos)
    nombre_cliente TEXT NOT NULL, -- Nombre descriptivo de la cuenta (ej: "LaReina Pasteleria")
    nombre_visible TEXT NOT NULL, -- Nombre del cliente (ej: "aura")
    empresa_id UUID REFERENCES cliente_empresas(id) ON DELETE SET NULL, -- Empresa vinculada (opcional)
    conectada BOOLEAN DEFAULT true, -- Si la cuenta está conectada
    account_status INTEGER DEFAULT 1, -- Estado de la cuenta (1=activa, 0=inactiva)
    activa BOOLEAN DEFAULT true, -- Si la cuenta está activa para reportes
    
    -- Información adicional de la cuenta (cache de datos de Google Ads API)
    moneda TEXT DEFAULT 'MXN',
    zona_horaria TEXT DEFAULT 'America/Mexico_City',
    es_test BOOLEAN DEFAULT false,
    accesible BOOLEAN DEFAULT true,
    problema TEXT, -- Descripción del problema si no es accesible
    
    -- Estadísticas de anuncios (cache)
    ads_activos INTEGER DEFAULT 0,
    anuncios_activos INTEGER DEFAULT 0,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW(),
    CREATED_AT TIMESTAMP DEFAULT NOW(),
    UPDATED_AT TIMESTAMP DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_customer_id ON google_ads_cuentas(customer_id);
CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_nombre_visible ON google_ads_cuentas(nombre_visible);
CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_empresa_id ON google_ads_cuentas(empresa_id);
CREATE INDEX IF NOT EXISTS idx_google_ads_cuentas_activa ON google_ads_cuentas(activa);

-- Comentarios para documentación
COMMENT ON TABLE google_ads_cuentas IS 'Tabla principal de cuentas de Google Ads, similar a meta_ads_cuentas. Almacena la información de las cuentas y su vinculación opcional con empresas.';
COMMENT ON COLUMN google_ads_cuentas.customer_id IS 'ID de la cuenta de Google Ads (Customer ID de 10 dígitos)';
COMMENT ON COLUMN google_ads_cuentas.nombre_visible IS 'Nombre del cliente (ej: aura) para filtrar las cuentas por cliente';
COMMENT ON COLUMN google_ads_cuentas.empresa_id IS 'ID de la empresa vinculada en la tabla cliente_empresas (opcional)';
COMMENT ON COLUMN google_ads_cuentas.accesible IS 'Si la cuenta es accesible desde la API de Google Ads';
COMMENT ON COLUMN google_ads_cuentas.problema IS 'Descripción del problema si la cuenta no es accesible (ej: deuda, suspendida)';

-- Trigger para actualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION update_google_ads_cuentas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    NEW.UPDATED_AT = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_google_ads_cuentas_updated_at
    BEFORE UPDATE ON google_ads_cuentas
    FOR EACH ROW
    EXECUTE FUNCTION update_google_ads_cuentas_updated_at();
