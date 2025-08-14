-- Script para verificar y agregar columnas de estadísticas para webhooks Meta Ads
-- Ejecutar en Supabase SQL Editor

-- 1. VERIFICAR SI EXISTE UNA TABLA DE ESTADÍSTICAS WEBHOOKS
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('estadisticas_webhooks', 'webhooks_estadisticas', 'meta_webhooks_stats')
ORDER BY table_name, ordinal_position;

-- 2. VERIFICAR COLUMNAS EN TABLA meta_ads_cuentas
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'meta_ads_cuentas'
ORDER BY ordinal_position;

-- 3. VERIFICAR COLUMNAS EN TABLA logs_webhooks_meta
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'logs_webhooks_meta'
ORDER BY ordinal_position;

-- 4. CREAR TABLA DE ESTADÍSTICAS WEBHOOKS (si no existe)
CREATE TABLE IF NOT EXISTS estadisticas_webhooks (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL,
    total_cuentas INTEGER DEFAULT 0,
    con_webhook INTEGER DEFAULT 0,
    sin_webhook INTEGER DEFAULT 0,
    cuentas_activas INTEGER DEFAULT 0,
    eventos_24h INTEGER DEFAULT 0,
    publicaciones_24h INTEGER DEFAULT 0,
    errores_24h INTEGER DEFAULT 0,
    tokens_validos INTEGER DEFAULT 0,
    ultima_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    creada_en TIMESTAMPTZ DEFAULT NOW()
);

-- 5. AGREGAR ÍNDICES PARA OPTIMIZACIÓN
CREATE INDEX IF NOT EXISTS idx_estadisticas_webhooks_nora 
ON estadisticas_webhooks(nombre_nora);

CREATE INDEX IF NOT EXISTS idx_estadisticas_webhooks_fecha 
ON estadisticas_webhooks(ultima_actualizacion DESC);

-- 6. INSERTAR DATOS INICIALES PARA AURA (si no existen)
INSERT INTO estadisticas_webhooks (nombre_nora, total_cuentas, con_webhook, sin_webhook, cuentas_activas)
SELECT 
    'aura' as nombre_nora,
    COUNT(*) as total_cuentas,
    COUNT(*) FILTER (WHERE webhook_registrado = true) as con_webhook,
    COUNT(*) FILTER (WHERE webhook_registrado = false OR webhook_registrado IS NULL) as sin_webhook,
    COUNT(*) FILTER (WHERE estado_actual = 'ACTIVE') as cuentas_activas
FROM meta_ads_cuentas
WHERE NOT EXISTS (
    SELECT 1 FROM estadisticas_webhooks WHERE nombre_nora = 'aura'
);

-- 7. VERIFICAR DATOS INSERTADOS
SELECT * FROM estadisticas_webhooks WHERE nombre_nora = 'aura';

-- 8. CONTAR DATOS ACTUALES PARA VERIFICACIÓN
SELECT 
    'meta_ads_cuentas' as tabla,
    COUNT(*) as total_registros
FROM meta_ads_cuentas

UNION ALL

SELECT 
    'logs_webhooks_meta' as tabla,
    COUNT(*) as total_registros
FROM logs_webhooks_meta

UNION ALL

SELECT 
    'estadisticas_webhooks' as tabla,
    COUNT(*) as total_registros
FROM estadisticas_webhooks;

-- 9. FUNCIÓN PARA ACTUALIZAR ESTADÍSTICAS AUTOMÁTICAMENTE
CREATE OR REPLACE FUNCTION actualizar_estadisticas_webhooks(p_nombre_nora VARCHAR(50))
RETURNS VOID AS $$
DECLARE
    v_total_cuentas INTEGER;
    v_con_webhook INTEGER;
    v_sin_webhook INTEGER;
    v_cuentas_activas INTEGER;
    v_eventos_24h INTEGER;
    v_publicaciones_24h INTEGER;
BEGIN
    -- Calcular estadísticas de cuentas
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE webhook_registrado = true),
        COUNT(*) FILTER (WHERE webhook_registrado = false OR webhook_registrado IS NULL),
        COUNT(*) FILTER (WHERE estado_actual = 'ACTIVE')
    INTO v_total_cuentas, v_con_webhook, v_sin_webhook, v_cuentas_activas
    FROM meta_ads_cuentas;

    -- Calcular eventos últimas 24h
    SELECT COUNT(*)
    INTO v_eventos_24h
    FROM logs_webhooks_meta
    WHERE timestamp >= NOW() - INTERVAL '24 hours';

    -- Insertar o actualizar estadísticas
    INSERT INTO estadisticas_webhooks (
        nombre_nora, total_cuentas, con_webhook, sin_webhook, 
        cuentas_activas, eventos_24h, ultima_actualizacion
    ) VALUES (
        p_nombre_nora, v_total_cuentas, v_con_webhook, v_sin_webhook,
        v_cuentas_activas, v_eventos_24h, NOW()
    )
    ON CONFLICT (nombre_nora) 
    DO UPDATE SET
        total_cuentas = EXCLUDED.total_cuentas,
        con_webhook = EXCLUDED.con_webhook,
        sin_webhook = EXCLUDED.sin_webhook,
        cuentas_activas = EXCLUDED.cuentas_activas,
        eventos_24h = EXCLUDED.eventos_24h,
        ultima_actualizacion = NOW();
END;
$$ LANGUAGE plpgsql;

-- 10. AGREGAR CONSTRAINT ÚNICO PARA nombre_nora
ALTER TABLE estadisticas_webhooks 
ADD CONSTRAINT uk_estadisticas_webhooks_nora 
UNIQUE (nombre_nora);

-- 11. EJECUTAR FUNCIÓN PARA ACTUALIZAR DATOS
SELECT actualizar_estadisticas_webhooks('aura');

-- 12. VERIFICACIÓN FINAL
SELECT 
    nombre_nora,
    total_cuentas,
    con_webhook,
    sin_webhook,
    cuentas_activas,
    eventos_24h,
    ultima_actualizacion
FROM estadisticas_webhooks 
WHERE nombre_nora = 'aura';
