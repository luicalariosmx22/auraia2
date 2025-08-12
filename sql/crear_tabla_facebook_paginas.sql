-- Crear tabla para páginas de Facebook
CREATE TABLE IF NOT EXISTS facebook_paginas (
    id SERIAL PRIMARY KEY,
    page_id VARCHAR(50) UNIQUE NOT NULL,
    nombre_pagina VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    categoria VARCHAR(100),
    descripcion TEXT,
    seguidores INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    website VARCHAR(500),
    telefono VARCHAR(50),
    email VARCHAR(100),
    direccion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    foto_perfil_url TEXT,
    foto_portada_url TEXT,
    verificada BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    
    -- Estado para webhook (similar a cuentas publicitarias)
    estado_webhook VARCHAR(20) DEFAULT 'activa' CHECK (estado_webhook IN ('activa', 'pausada', 'excluida')),
    
    -- Campos de control
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Metadatos adicionales
    access_token_valido BOOLEAN DEFAULT TRUE,
    access_token TEXT, -- Token de acceso específico de cada página
    ultima_sincronizacion TIMESTAMP WITH TIME ZONE,
    permisos_disponibles TEXT[], -- Array de permisos que tiene la app
    
    -- Información del cliente (opcional)
    nombre_cliente VARCHAR(255),
    empresa VARCHAR(255),
    
    CONSTRAINT unique_page_id UNIQUE (page_id)
);

-- Índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_facebook_paginas_page_id ON facebook_paginas(page_id);
CREATE INDEX IF NOT EXISTS idx_facebook_paginas_estado ON facebook_paginas(estado_webhook);
CREATE INDEX IF NOT EXISTS idx_facebook_paginas_activa ON facebook_paginas(activa);
CREATE INDEX IF NOT EXISTS idx_facebook_paginas_nombre ON facebook_paginas(nombre_pagina);

-- Trigger para actualizar campo actualizado_en
CREATE OR REPLACE FUNCTION update_facebook_paginas_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Eliminar trigger existente si existe y crear uno nuevo
DROP TRIGGER IF EXISTS trigger_update_facebook_paginas_timestamp ON facebook_paginas;
CREATE TRIGGER trigger_update_facebook_paginas_timestamp
    BEFORE UPDATE ON facebook_paginas
    FOR EACH ROW
    EXECUTE FUNCTION update_facebook_paginas_timestamp();

-- Comentarios para documentación
COMMENT ON TABLE facebook_paginas IS 'Páginas de Facebook administradas para webhooks y automatización';
COMMENT ON COLUMN facebook_paginas.page_id IS 'ID único de la página en Facebook';
COMMENT ON COLUMN facebook_paginas.estado_webhook IS 'Estado para recibir webhooks: activa, pausada, excluida';
COMMENT ON COLUMN facebook_paginas.permisos_disponibles IS 'Array de permisos que tiene la app para esta página';
COMMENT ON COLUMN facebook_paginas.access_token_valido IS 'Indica si el token de acceso sigue siendo válido';
