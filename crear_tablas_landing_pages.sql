-- Tabla para configuración principal de landing pages
CREATE TABLE IF NOT EXISTS landing_pages_config (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL,
    titulo VARCHAR(200),
    subtitulo TEXT,
    cta_texto VARCHAR(100),
    cta_url VARCHAR(500),
    color_primario VARCHAR(7) DEFAULT '#3B82F6',
    color_secundario VARCHAR(7) DEFAULT '#1E40AF',
    color_texto VARCHAR(7) DEFAULT '#1F2937',
    bloques JSON DEFAULT '["hero", "caracteristicas", "servicios", "testimonios", "contacto"]',
    seo_descripcion TEXT,
    seo_keywords TEXT,
    publicada BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    creada_en TIMESTAMPTZ DEFAULT NOW(),
    actualizada_en TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla para bloques/secciones personalizadas
CREATE TABLE IF NOT EXISTS landing_pages_bloques (
    id BIGSERIAL PRIMARY KEY,
    config_id BIGINT REFERENCES landing_pages_config(id) ON DELETE CASCADE,
    tipo_bloque VARCHAR(50) NOT NULL, -- hero, caracteristicas, servicios, testimonios, contacto, custom
    titulo VARCHAR(200),
    subtitulo TEXT,
    contenido JSON,
    orden INTEGER DEFAULT 0,
    visible BOOLEAN DEFAULT TRUE,
    creada_en TIMESTAMPTZ DEFAULT NOW(),
    actualizada_en TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_landing_pages_config_nora ON landing_pages_config(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_landing_pages_config_activa ON landing_pages_config(activa);
CREATE INDEX IF NOT EXISTS idx_landing_pages_config_publicada ON landing_pages_config(publicada);
CREATE INDEX IF NOT EXISTS idx_landing_pages_bloques_config ON landing_pages_bloques(config_id);
CREATE INDEX IF NOT EXISTS idx_landing_pages_bloques_tipo ON landing_pages_bloques(tipo_bloque);
CREATE INDEX IF NOT EXISTS idx_landing_pages_bloques_orden ON landing_pages_bloques(orden);

-- Insertar configuración por defecto para 'aura'
INSERT INTO landing_pages_config (
    nombre_nora, 
    titulo, 
    subtitulo, 
    cta_texto, 
    cta_url,
    seo_descripcion,
    seo_keywords,
    bloques
) VALUES (
    'aura',
    'Aura - Marketing Digital Inteligente',
    'Transformamos tu negocio con estrategias de marketing digital basadas en inteligencia artificial',
    'Comenzar Ahora',
    '#contacto',
    'Aura es tu aliado en marketing digital. Ofrecemos estrategias personalizadas, automatización inteligente y resultados medibles para hacer crecer tu negocio.',
    'marketing digital, inteligencia artificial, automatización, estrategias digitales, growth marketing',
    '["hero", "caracteristicas", "servicios", "testimonios", "contacto"]'
) ON CONFLICT DO NOTHING;

-- Insertar bloques por defecto para 'aura'
WITH aura_config AS (
    SELECT id FROM landing_pages_config WHERE nombre_nora = 'aura' LIMIT 1
)
INSERT INTO landing_pages_bloques (config_id, tipo_bloque, titulo, subtitulo, contenido, orden) 
SELECT 
    ac.id,
    'caracteristicas',
    '¿Por qué elegir Aura?',
    'La combinación perfecta de tecnología e inteligencia para tu éxito digital',
    '{
        "items": [
            {
                "icono": "⚡",
                "titulo": "Automatización Inteligente",
                "descripcion": "IA que optimiza tus campañas 24/7"
            },
            {
                "icono": "📊",
                "titulo": "Análisis Profundo",
                "descripcion": "Insights accionables de tus datos"
            },
            {
                "icono": "🎯",
                "titulo": "Targeting Preciso",
                "descripcion": "Llega exactamente a tu audiencia ideal"
            }
        ]
    }'::json,
    1
FROM aura_config ac
UNION ALL
SELECT 
    ac.id,
    'servicios',
    'Nuestros Servicios',
    'Todo lo que necesitas para dominar el mundo digital',
    '{
        "items": [
            {
                "icono": "🚀",
                "titulo": "Meta Ads Management",
                "descripcion": "Gestión profesional de Facebook e Instagram Ads",
                "precio": "Desde $2,500/mes"
            },
            {
                "icono": "📱",
                "titulo": "WhatsApp Business",
                "descripcion": "Automatización y gestión de conversaciones",
                "precio": "Desde $1,500/mes"
            },
            {
                "icono": "📈",
                "titulo": "Google Ads",
                "descripcion": "Campañas optimizadas en Google Search y Display",
                "precio": "Desde $3,000/mes"
            }
        ]
    }'::json,
    2
FROM aura_config ac
UNION ALL
SELECT 
    ac.id,
    'testimonios',
    'Casos de Éxito',
    'Historias reales de crecimiento y transformación digital',
    '{
        "items": [
            {
                "nombre": "Carlos Mendoza",
                "empresa": "TechStart México",
                "testimonio": "Con Aura aumentamos nuestras conversions 300% en solo 3 meses. Su sistema de IA es increíble.",
                "rating": 5
            },
            {
                "nombre": "Ana García",
                "empresa": "Fashion Boutique",
                "testimonio": "El ROI mejoró drasticamente. Ahora sabemos exactamente dónde invertir nuestro presupuesto de marketing.",
                "rating": 5
            },
            {
                "nombre": "Roberto Silva",
                "empresa": "Consulting Pro",
                "testimonio": "La automatización de WhatsApp nos permitió atender 5x más clientes sin aumentar personal.",
                "rating": 5
            }
        ]
    }'::json,
    3
FROM aura_config ac
WHERE NOT EXISTS (
    SELECT 1 FROM landing_pages_bloques lb 
    WHERE lb.config_id = ac.id
);

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_landing_pages_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizada_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar timestamp automáticamente
DROP TRIGGER IF EXISTS trigger_update_landing_pages_config_updated_at ON landing_pages_config;
CREATE TRIGGER trigger_update_landing_pages_config_updated_at
    BEFORE UPDATE ON landing_pages_config
    FOR EACH ROW
    EXECUTE FUNCTION update_landing_pages_updated_at();

DROP TRIGGER IF EXISTS trigger_update_landing_pages_bloques_updated_at ON landing_pages_bloques;
CREATE TRIGGER trigger_update_landing_pages_bloques_updated_at
    BEFORE UPDATE ON landing_pages_bloques
    FOR EACH ROW
    EXECUTE FUNCTION update_landing_pages_updated_at();

-- Verificar que las tablas se crearon correctamente
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('landing_pages_config', 'landing_pages_bloques')
ORDER BY table_name, ordinal_position;
