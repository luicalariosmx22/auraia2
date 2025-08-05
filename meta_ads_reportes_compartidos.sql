-- Script SQL para crear la tabla de reportes compartidos de Meta Ads
-- Ejecutar en Supabase SQL Editor

CREATE TABLE IF NOT EXISTS meta_ads_reportes_compartidos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporte_id UUID NOT NULL REFERENCES meta_ads_reportes_semanales(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    empresa_nombre VARCHAR(255) DEFAULT '',
    periodo VARCHAR(100) DEFAULT '',
    compartido_por VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE,
    
    -- Índices para mejorar performance
    UNIQUE(id, token)
);

-- Crear índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_compartidos_token 
ON meta_ads_reportes_compartidos(token);

CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_compartidos_reporte_id 
ON meta_ads_reportes_compartidos(reporte_id);

CREATE INDEX IF NOT EXISTS idx_meta_ads_reportes_compartidos_activo 
ON meta_ads_reportes_compartidos(activo);

-- Agregar comentarios para documentación
COMMENT ON TABLE meta_ads_reportes_compartidos IS 'Tabla para gestionar enlaces públicos compartidos de reportes Meta Ads';
COMMENT ON COLUMN meta_ads_reportes_compartidos.id IS 'UUID único que se usa en la URL pública';
COMMENT ON COLUMN meta_ads_reportes_compartidos.token IS 'Token de seguridad para validar acceso al reporte';
COMMENT ON COLUMN meta_ads_reportes_compartidos.reporte_id IS 'ID del reporte semanal que se está compartiendo';
COMMENT ON COLUMN meta_ads_reportes_compartidos.empresa_nombre IS 'Nombre de la empresa para mostrar en el enlace';
COMMENT ON COLUMN meta_ads_reportes_compartidos.periodo IS 'Descripción del periodo del reporte';
COMMENT ON COLUMN meta_ads_reportes_compartidos.compartido_por IS 'Usuario que generó el enlace compartido';
COMMENT ON COLUMN meta_ads_reportes_compartidos.activo IS 'Si el enlace está activo o deshabilitado';

-- Opcional: Políticas RLS si se requiere
-- ALTER TABLE meta_ads_reportes_compartidos ENABLE ROW LEVEL SECURITY;
