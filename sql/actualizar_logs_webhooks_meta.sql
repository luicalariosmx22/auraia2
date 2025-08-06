-- Script para actualizar tabla logs_webhooks_meta
-- Agregar campos necesarios para unificar con meta_webhook_eventos

-- Agregar campo procesado si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'logs_webhooks_meta' 
        AND column_name = 'procesado'
    ) THEN
        ALTER TABLE logs_webhooks_meta ADD COLUMN procesado BOOLEAN DEFAULT false;
        COMMENT ON COLUMN logs_webhooks_meta.procesado IS 'Indica si el evento ha sido procesado';
    END IF;
END $$;

-- Agregar campo procesado_en si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'logs_webhooks_meta' 
        AND column_name = 'procesado_en'
    ) THEN
        ALTER TABLE logs_webhooks_meta ADD COLUMN procesado_en TIMESTAMP WITH TIME ZONE;
        COMMENT ON COLUMN logs_webhooks_meta.procesado_en IS 'Fecha y hora cuando fue procesado el evento';
    END IF;
END $$;

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_logs_webhooks_meta_procesado ON logs_webhooks_meta(procesado);
CREATE INDEX IF NOT EXISTS idx_logs_webhooks_meta_timestamp ON logs_webhooks_meta(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_webhooks_meta_tipo_objeto ON logs_webhooks_meta(tipo_objeto);

-- Comentario sobre la unificación
COMMENT ON TABLE logs_webhooks_meta IS 'Tabla unificada para registro y procesamiento de eventos webhook de Meta Ads';

-- Mostrar estructura actualizada
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    COALESCE(col_description(pgc.oid, pa.attnum), '') as description
FROM information_schema.columns ic
LEFT JOIN pg_class pgc ON pgc.relname = ic.table_name
LEFT JOIN pg_attribute pa ON pa.attrelid = pgc.oid AND pa.attname = ic.column_name
WHERE ic.table_name = 'logs_webhooks_meta'
ORDER BY ic.ordinal_position;
