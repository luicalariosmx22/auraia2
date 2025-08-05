-- Tablas para sistema de automatización de campañas basado en publicaciones

-- Tabla para configuración de automatizaciones
CREATE TABLE IF NOT EXISTS meta_ads_automatizaciones (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    page_id VARCHAR(50) NOT NULL, -- ID de la página de Facebook/Instagram
    ad_account_id VARCHAR(50) NOT NULL, -- ID de la cuenta publicitaria
    campaign_id VARCHAR(50) NOT NULL, -- ID de la campaña objetivo
    adset_id VARCHAR(50) NOT NULL, -- ID del conjunto de anuncios objetivo
    reglas_json JSONB NOT NULL DEFAULT '{}', -- Reglas de filtrado y configuración
    activa BOOLEAN DEFAULT true,
    creada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT meta_ads_automatizaciones_page_id_check CHECK (page_id != ''),
    CONSTRAINT meta_ads_automatizaciones_ad_account_id_check CHECK (ad_account_id != ''),
    CONSTRAINT meta_ads_automatizaciones_campaign_id_check CHECK (campaign_id != ''),
    CONSTRAINT meta_ads_automatizaciones_adset_id_check CHECK (adset_id != ''),
    
    -- Relación con cuentas de Meta Ads
    FOREIGN KEY (ad_account_id) REFERENCES meta_ads_cuentas(id_cuenta_publicitaria)
);

-- Índices para meta_ads_automatizaciones
CREATE INDEX IF NOT EXISTS idx_meta_ads_automatizaciones_nora ON meta_ads_automatizaciones(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_meta_ads_automatizaciones_page_id ON meta_ads_automatizaciones(page_id);
CREATE INDEX IF NOT EXISTS idx_meta_ads_automatizaciones_activa ON meta_ads_automatizaciones(activa);
CREATE INDEX IF NOT EXISTS idx_meta_ads_automatizaciones_created ON meta_ads_automatizaciones(creada_en);

-- Tabla para registro de publicaciones recibidas por webhook
CREATE TABLE IF NOT EXISTS meta_publicaciones_webhook (
    id BIGSERIAL PRIMARY KEY,
    page_id VARCHAR(50) NOT NULL,
    post_id VARCHAR(100) NOT NULL UNIQUE, -- ID único de la publicación
    mensaje TEXT,
    tipo_item VARCHAR(50), -- 'post', 'photo', 'video', etc.
    created_time BIGINT, -- Timestamp Unix de creación en Meta
    webhook_data JSONB, -- Datos completos del webhook
    procesada BOOLEAN DEFAULT false,
    procesada_en TIMESTAMP WITH TIME ZONE,
    creada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT meta_publicaciones_webhook_page_id_check CHECK (page_id != ''),
    CONSTRAINT meta_publicaciones_webhook_post_id_check CHECK (post_id != '')
);

-- Índices para meta_publicaciones_webhook
CREATE INDEX IF NOT EXISTS idx_meta_publicaciones_webhook_page_id ON meta_publicaciones_webhook(page_id);
CREATE INDEX IF NOT EXISTS idx_meta_publicaciones_webhook_procesada ON meta_publicaciones_webhook(procesada);
CREATE INDEX IF NOT EXISTS idx_meta_publicaciones_webhook_created ON meta_publicaciones_webhook(creada_en);
CREATE INDEX IF NOT EXISTS idx_meta_publicaciones_webhook_post_created ON meta_publicaciones_webhook(created_time);

-- Tabla para registro de anuncios creados automáticamente
CREATE TABLE IF NOT EXISTS meta_anuncios_automatizados (
    id BIGSERIAL PRIMARY KEY,
    automatizacion_id BIGINT NOT NULL,
    post_id VARCHAR(100) NOT NULL, -- ID de la publicación que originó el anuncio
    ad_id VARCHAR(50) NOT NULL, -- ID del anuncio creado en Meta
    creative_id VARCHAR(50), -- ID del creative creado
    nombre_anuncio VARCHAR(200),
    mensaje_original TEXT, -- Contenido original de la publicación
    detalles_publicacion JSONB, -- Detalles adicionales de la publicación
    estado_anuncio VARCHAR(20) DEFAULT 'ACTIVE', -- Estado actual del anuncio
    metricas_anuncio JSONB, -- Métricas del anuncio (se actualiza periódicamente)
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Relaciones
    FOREIGN KEY (automatizacion_id) REFERENCES meta_ads_automatizaciones(id) ON DELETE CASCADE,
    
    -- Índices
    CONSTRAINT meta_anuncios_automatizados_ad_id_check CHECK (ad_id != ''),
    CONSTRAINT meta_anuncios_automatizados_post_id_check CHECK (post_id != '')
);

-- Índices para meta_anuncios_automatizados
CREATE INDEX IF NOT EXISTS idx_meta_anuncios_automatizados_automatizacion ON meta_anuncios_automatizados(automatizacion_id);
CREATE INDEX IF NOT EXISTS idx_meta_anuncios_automatizados_post_id ON meta_anuncios_automatizados(post_id);
CREATE INDEX IF NOT EXISTS idx_meta_anuncios_automatizados_ad_id ON meta_anuncios_automatizados(ad_id);
CREATE INDEX IF NOT EXISTS idx_meta_anuncios_automatizados_created ON meta_anuncios_automatizados(creado_en);
CREATE INDEX IF NOT EXISTS idx_meta_anuncios_automatizados_estado ON meta_anuncios_automatizados(estado_anuncio);

-- Tabla para configuración de páginas y webhooks
CREATE TABLE IF NOT EXISTS meta_paginas_webhook (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(100) NOT NULL,
    page_id VARCHAR(50) NOT NULL UNIQUE,
    page_name VARCHAR(200),
    page_access_token TEXT, -- Token de acceso de la página
    webhook_verificado BOOLEAN DEFAULT false,
    webhook_activo BOOLEAN DEFAULT true,
    campos_suscritos TEXT[], -- Array de campos suscritos al webhook
    ultima_verificacion TIMESTAMP WITH TIME ZONE,
    creada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT meta_paginas_webhook_page_id_check CHECK (page_id != ''),
    CONSTRAINT meta_paginas_webhook_nora_check CHECK (nombre_nora != '')
);

-- Índices para meta_paginas_webhook
CREATE INDEX IF NOT EXISTS idx_meta_paginas_webhook_nora ON meta_paginas_webhook(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_meta_paginas_webhook_page_id ON meta_paginas_webhook(page_id);
CREATE INDEX IF NOT EXISTS idx_meta_paginas_webhook_activo ON meta_paginas_webhook(webhook_activo);

-- Tabla para plantillas de anuncios automatizados
CREATE TABLE IF NOT EXISTS meta_plantillas_anuncios (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    plantilla_json JSONB NOT NULL DEFAULT '{}', -- Configuración de la plantilla
    activa BOOLEAN DEFAULT true,
    creada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizada_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT meta_plantillas_anuncios_nombre_check CHECK (nombre != ''),
    CONSTRAINT meta_plantillas_anuncios_nora_check CHECK (nombre_nora != '')
);

-- Índices para meta_plantillas_anuncios
CREATE INDEX IF NOT EXISTS idx_meta_plantillas_anuncios_nora ON meta_plantillas_anuncios(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_meta_plantillas_anuncios_activa ON meta_plantillas_anuncios(activa);

-- Comentarios en las tablas
COMMENT ON TABLE meta_ads_automatizaciones IS 'Configuración de automatizaciones para crear anuncios desde publicaciones';
COMMENT ON TABLE meta_publicaciones_webhook IS 'Registro de publicaciones recibidas por webhook de Meta';
COMMENT ON TABLE meta_anuncios_automatizados IS 'Historial de anuncios creados automáticamente';
COMMENT ON TABLE meta_paginas_webhook IS 'Configuración de páginas y webhooks de Meta';
COMMENT ON TABLE meta_plantillas_anuncios IS 'Plantillas para anuncios automatizados';

-- Comentarios en columnas importantes
COMMENT ON COLUMN meta_ads_automatizaciones.reglas_json IS 'JSON con filtros_contenido, plantilla_anuncio y programacion';
COMMENT ON COLUMN meta_publicaciones_webhook.webhook_data IS 'Datos completos recibidos del webhook de Meta';
COMMENT ON COLUMN meta_anuncios_automatizados.detalles_publicacion IS 'Detalles adicionales obtenidos de Graph API';
COMMENT ON COLUMN meta_anuncios_automatizados.metricas_anuncio IS 'Métricas del anuncio (impresiones, clicks, etc.)';
COMMENT ON COLUMN meta_plantillas_anuncios.plantilla_json IS 'Configuración de texto, imágenes, CTA, etc.';
