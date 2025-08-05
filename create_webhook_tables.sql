-- Tabla para registrar todos los eventos de webhook recibidos de Meta Ads
CREATE TABLE IF NOT EXISTS public.meta_webhook_eventos (
    id SERIAL PRIMARY KEY,
    objeto TEXT NOT NULL,
    objeto_id TEXT NOT NULL,
    campo TEXT NOT NULL,
    valor TEXT,
    hora_evento TIMESTAMP WITH TIME ZONE NOT NULL,
    procesado BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_procesamiento TEXT,
    intentos_procesamiento INTEGER DEFAULT 0
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_meta_webhook_eventos_objeto ON public.meta_webhook_eventos(objeto, objeto_id);
CREATE INDEX IF NOT EXISTS idx_meta_webhook_eventos_procesado ON public.meta_webhook_eventos(procesado);
CREATE INDEX IF NOT EXISTS idx_meta_webhook_eventos_fecha ON public.meta_webhook_eventos(hora_evento);

-- Tabla para logs de webhooks (más simple, para debugging)
CREATE TABLE IF NOT EXISTS public.logs_webhooks_meta (
    id SERIAL PRIMARY KEY,
    tipo_objeto TEXT NOT NULL,
    objeto_id TEXT NOT NULL,
    campo TEXT NOT NULL,
    valor TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para logs
CREATE INDEX IF NOT EXISTS idx_logs_webhooks_meta_timestamp ON public.logs_webhooks_meta(timestamp);
