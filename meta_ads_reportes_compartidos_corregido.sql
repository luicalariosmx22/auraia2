-- Script SQL ACTUALIZADO para crear la tabla de reportes compartidos de Meta Ads
-- Ejecutar en Supabase SQL Editor
-- VERSIÓN CORREGIDA: reporte_id como UUID

-- Eliminar tabla si existe (solo para recrear con tipo correcto)
DROP TABLE IF EXISTS meta_ads_reportes_compartidos;

CREATE TABLE meta_ads_reportes_compartidos (
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
CREATE INDEX idx_meta_ads_reportes_compartidos_token 
ON meta_ads_reportes_compartidos(token);

CREATE INDEX idx_meta_ads_reportes_compartidos_reporte_id 
ON meta_ads_reportes_compartidos(reporte_id);

CREATE INDEX idx_meta_ads_reportes_compartidos_activo 
ON meta_ads_reportes_compartidos(activo);

-- Crear índice compuesto para búsquedas por ID + token
CREATE INDEX idx_meta_ads_reportes_compartidos_id_token_activo
ON meta_ads_reportes_compartidos(id, token, activo);

-- Agregar comentarios para documentación
COMMENT ON TABLE meta_ads_reportes_compartidos IS 'Tabla para gestionar enlaces públicos compartidos de reportes Meta Ads';
COMMENT ON COLUMN meta_ads_reportes_compartidos.id IS 'UUID único que se usa en la URL pública';
COMMENT ON COLUMN meta_ads_reportes_compartidos.token IS 'Token de seguridad para validar acceso al reporte';
COMMENT ON COLUMN meta_ads_reportes_compartidos.reporte_id IS 'UUID del reporte semanal que se está compartiendo';
COMMENT ON COLUMN meta_ads_reportes_compartidos.empresa_nombre IS 'Nombre de la empresa para mostrar en el enlace';
COMMENT ON COLUMN meta_ads_reportes_compartidos.periodo IS 'Descripción del periodo del reporte';
COMMENT ON COLUMN meta_ads_reportes_compartidos.compartido_por IS 'Usuario que generó el enlace compartido';
COMMENT ON COLUMN meta_ads_reportes_compartidos.activo IS 'Si el enlace está activo o deshabilitado';

-- Políticas RLS (Row Level Security) - opcional
-- ALTER TABLE meta_ads_reportes_compartidos ENABLE ROW LEVEL SECURITY;

-- Verificar que la tabla se creó correctamente
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'meta_ads_reportes_compartidos' 
ORDER BY ordinal_position;
