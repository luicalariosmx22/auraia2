-- =========================================================================
-- ACTUALIZACIÓN ESTRUCTURA DE TABLA logs_webhooks_meta
-- =========================================================================
-- Fecha: 2025-01-11
-- Propósito: Implementar estructura completa para logs_webhooks_meta
-- Estado: La tabla existe pero está vacía (sin estructura adecuada)
-- 
-- ⚠️ IMPORTANTE: Ejecutar en Supabase Dashboard → SQL Editor
-- =========================================================================

-- PASO 1: Verificar estado actual de la tabla
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default 
FROM information_schema.columns 
WHERE table_name = 'logs_webhooks_meta' 
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- PASO 2: Si la tabla está vacía o mal estructurada, recrearla
DROP TABLE IF EXISTS logs_webhooks_meta CASCADE;

-- PASO 3: Crear tabla con estructura completa
CREATE TABLE logs_webhooks_meta (
    -- Identificación primaria
    id BIGSERIAL PRIMARY KEY,
    
    -- Información del objeto webhook
    tipo_objeto VARCHAR(50) NOT NULL,                    -- 'campaign', 'ad', 'adset', 'audience', 'account'
    objeto_id VARCHAR(100) NOT NULL,                     -- ID del objeto (campaign_id, ad_id, etc.)
    campo VARCHAR(100),                                  -- Campo que cambió ('status', 'name', etc.)
    valor TEXT,                                          -- Nuevo valor del campo
    
    -- Timestamps y control
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),       -- Cuando ocurrió el evento
    recibido_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),     -- Cuando llegó al webhook
    
    -- Información de contexto
    nombre_nora VARCHAR(50),                             -- A qué Nora pertenece
    id_cuenta_publicitaria VARCHAR(100),                -- Cuenta Meta Ads asociada
    
    -- Control de procesamiento
    procesado BOOLEAN NOT NULL DEFAULT FALSE,           -- Si el evento fue procesado
    procesado_en TIMESTAMPTZ,                           -- Cuándo fue procesado
    
    -- Datos adicionales
    datos_adicionales JSON,                             -- Información extra del webhook
    error_procesamiento TEXT,                           -- Error si hubo problemas
    
    -- Metadatos
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- PASO 4: Crear índices para optimización de consultas
CREATE INDEX idx_logs_webhooks_meta_tipo_objeto ON logs_webhooks_meta(tipo_objeto);
CREATE INDEX idx_logs_webhooks_meta_objeto_id ON logs_webhooks_meta(objeto_id);
CREATE INDEX idx_logs_webhooks_meta_timestamp ON logs_webhooks_meta(timestamp DESC);
CREATE INDEX idx_logs_webhooks_meta_recibido_en ON logs_webhooks_meta(recibido_en DESC);
CREATE INDEX idx_logs_webhooks_meta_nombre_nora ON logs_webhooks_meta(nombre_nora);
CREATE INDEX idx_logs_webhooks_meta_cuenta ON logs_webhooks_meta(id_cuenta_publicitaria);
CREATE INDEX idx_logs_webhooks_meta_procesado ON logs_webhooks_meta(procesado);
CREATE INDEX idx_logs_webhooks_meta_no_procesados ON logs_webhooks_meta(procesado, timestamp) WHERE procesado = FALSE;

-- PASO 5: Crear trigger para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION actualizar_timestamp_logs_webhooks_meta()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_logs_webhooks_meta
    BEFORE UPDATE ON logs_webhooks_meta
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp_logs_webhooks_meta();

-- PASO 6: Configurar RLS (Row Level Security) si es necesario
ALTER TABLE logs_webhooks_meta ENABLE ROW LEVEL SECURITY;

-- Política para permitir acceso a todos los roles de servicio
CREATE POLICY logs_webhooks_meta_policy ON logs_webhooks_meta
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- PASO 7: Comentarios en tabla y columnas para documentación
COMMENT ON TABLE logs_webhooks_meta IS 'Registro de eventos recibidos de webhooks de Meta Ads';
COMMENT ON COLUMN logs_webhooks_meta.tipo_objeto IS 'Tipo de objeto: campaign, ad, adset, audience, account';
COMMENT ON COLUMN logs_webhooks_meta.objeto_id IS 'ID único del objeto que cambió';
COMMENT ON COLUMN logs_webhooks_meta.campo IS 'Campo específico que cambió en el objeto';
COMMENT ON COLUMN logs_webhooks_meta.valor IS 'Nuevo valor del campo que cambió';
COMMENT ON COLUMN logs_webhooks_meta.timestamp IS 'Timestamp del evento según Meta';
COMMENT ON COLUMN logs_webhooks_meta.recibido_en IS 'Timestamp cuando llegó al webhook';
COMMENT ON COLUMN logs_webhooks_meta.nombre_nora IS 'Identificador de la instancia Nora';
COMMENT ON COLUMN logs_webhooks_meta.id_cuenta_publicitaria IS 'ID de cuenta publicitaria Meta Ads';
COMMENT ON COLUMN logs_webhooks_meta.procesado IS 'Indica si el evento fue procesado por el sistema';
COMMENT ON COLUMN logs_webhooks_meta.procesado_en IS 'Timestamp de cuando fue procesado';
COMMENT ON COLUMN logs_webhooks_meta.datos_adicionales IS 'Datos JSON adicionales del webhook';
COMMENT ON COLUMN logs_webhooks_meta.error_procesamiento IS 'Mensaje de error si falló el procesamiento';

-- PASO 8: Verificar la estructura final
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'logs_webhooks_meta' 
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- PASO 9: Verificar índices creados
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'logs_webhooks_meta' 
    AND schemaname = 'public';

-- PASO 10: Test de inserción para verificar que funciona
INSERT INTO logs_webhooks_meta (
    tipo_objeto, 
    objeto_id, 
    campo, 
    valor, 
    nombre_nora, 
    id_cuenta_publicitaria
) VALUES (
    'campaign',
    'test_campaign_123',
    'status',
    'ACTIVE',
    'aura',
    '123456789'
);

-- Verificar que se insertó correctamente
SELECT * FROM logs_webhooks_meta ORDER BY id DESC LIMIT 1;

-- PASO 11: Limpiar test data
DELETE FROM logs_webhooks_meta WHERE objeto_id = 'test_campaign_123';

-- =========================================================================
-- ✅ ESTRUCTURA COMPLETADA
-- =========================================================================
-- La tabla logs_webhooks_meta ahora tiene la estructura completa necesaria
-- para el sistema de webhooks de Meta Ads.
--
-- ✅ Campos implementados:
-- - Identificación: id, tipo_objeto, objeto_id, campo, valor
-- - Timestamps: timestamp, recibido_en, creado_en, actualizado_en
-- - Contexto: nombre_nora, id_cuenta_publicitaria
-- - Control: procesado, procesado_en, error_procesamiento
-- - Datos: datos_adicionales (JSON)
--
-- ✅ Optimizaciones implementadas:
-- - 8 índices para consultas rápidas
-- - Trigger automático para actualizar timestamps
-- - RLS configurado para seguridad
-- - Comentarios para documentación
--
-- 🚀 Siguiente paso: Ejecutar este SQL en Supabase Dashboard
-- =========================================================================
