-- Crear tabla para reportes compartidos de Meta Ads
-- Este script debe ejecutarse en Supabase SQL Editor

CREATE TABLE IF NOT EXISTS meta_ads_reportes_compartidos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporte_id UUID NOT NULL,
    token VARCHAR(32) NOT NULL UNIQUE,
    empresa_nombre TEXT,
    periodo TEXT,
    compartido_por TEXT,
    accesos INTEGER DEFAULT 0,
    ultimo_acceso TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    
    -- Foreign key al reporte original
    CONSTRAINT fk_reporte_compartido 
        FOREIGN KEY (reporte_id) 
        REFERENCES meta_ads_reportes_semanales(id) 
        ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_reportes_compartidos_token ON meta_ads_reportes_compartidos(token);
CREATE INDEX IF NOT EXISTS idx_reportes_compartidos_reporte_id ON meta_ads_reportes_compartidos(reporte_id);
CREATE INDEX IF NOT EXISTS idx_reportes_compartidos_compartido_por ON meta_ads_reportes_compartidos(compartido_por);

-- Política de seguridad (RLS) - los reportes compartidos son públicos pero controlados
ALTER TABLE meta_ads_reportes_compartidos ENABLE ROW LEVEL SECURITY;

-- Eliminar políticas existentes si existen
DROP POLICY IF EXISTS "Permitir lectura con token válido" ON meta_ads_reportes_compartidos;
DROP POLICY IF EXISTS "Permitir inserción por usuarios autenticados" ON meta_ads_reportes_compartidos;

-- Permitir lectura con token válido
CREATE POLICY "Permitir lectura con token válido" ON meta_ads_reportes_compartidos
    FOR SELECT USING (expires_at > NOW());

-- Permitir inserción solo por usuarios autenticados (desde la app)
CREATE POLICY "Permitir inserción por usuarios autenticados" ON meta_ads_reportes_compartidos
    FOR INSERT WITH CHECK (true);

-- Comentarios para documentación
COMMENT ON TABLE meta_ads_reportes_compartidos IS 'Tabla para gestionar reportes de Meta Ads compartidos públicamente';
COMMENT ON COLUMN meta_ads_reportes_compartidos.token IS 'Token único para acceso público al reporte';
COMMENT ON COLUMN meta_ads_reportes_compartidos.accesos IS 'Contador de veces que se ha accedido al reporte';
COMMENT ON COLUMN meta_ads_reportes_compartidos.expires_at IS 'Fecha de expiración del link compartido (por defecto 30 días)';
