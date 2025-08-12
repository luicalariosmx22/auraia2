-- Script para asegurar que la tabla facebook_paginas tiene todas las columnas necesarias
-- para el manejo de tokens de acceso por página

-- Verificar si la tabla existe y agregar columnas faltantes si es necesario
DO $$
BEGIN
    -- Verificar y agregar columna access_token si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'facebook_paginas' 
        AND column_name = 'access_token'
    ) THEN
        ALTER TABLE public.facebook_paginas ADD COLUMN access_token TEXT NULL;
        RAISE NOTICE 'Columna access_token agregada a facebook_paginas';
    ELSE
        RAISE NOTICE 'Columna access_token ya existe en facebook_paginas';
    END IF;

    -- Verificar y agregar columna access_token_valido si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'facebook_paginas' 
        AND column_name = 'access_token_valido'
    ) THEN
        ALTER TABLE public.facebook_paginas ADD COLUMN access_token_valido BOOLEAN NULL DEFAULT TRUE;
        RAISE NOTICE 'Columna access_token_valido agregada a facebook_paginas';
    ELSE
        RAISE NOTICE 'Columna access_token_valido ya existe en facebook_paginas';
    END IF;

    -- Verificar y agregar columna ultima_sincronizacion si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'facebook_paginas' 
        AND column_name = 'ultima_sincronizacion'
    ) THEN
        ALTER TABLE public.facebook_paginas ADD COLUMN ultima_sincronizacion TIMESTAMP WITH TIME ZONE NULL;
        RAISE NOTICE 'Columna ultima_sincronizacion agregada a facebook_paginas';
    ELSE
        RAISE NOTICE 'Columna ultima_sincronizacion ya existe en facebook_paginas';
    END IF;
    
    -- Verificar y agregar columna permisos_disponibles si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'facebook_paginas' 
        AND column_name = 'permisos_disponibles'
    ) THEN
        ALTER TABLE public.facebook_paginas ADD COLUMN permisos_disponibles TEXT[] NULL;
        RAISE NOTICE 'Columna permisos_disponibles agregada a facebook_paginas';
    ELSE
        RAISE NOTICE 'Columna permisos_disponibles ya existe en facebook_paginas';
    END IF;
END $$;

-- Crear índices adicionales para optimizar consultas por token
CREATE INDEX IF NOT EXISTS idx_facebook_paginas_access_token_valido 
ON public.facebook_paginas USING btree (access_token_valido) 
TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_facebook_paginas_ultima_sincronizacion 
ON public.facebook_paginas USING btree (ultima_sincronizacion) 
TABLESPACE pg_default;

-- Comentarios en las nuevas columnas
COMMENT ON COLUMN public.facebook_paginas.access_token IS 'Token de acceso específico de la página para usar con la API de Facebook';
COMMENT ON COLUMN public.facebook_paginas.access_token_valido IS 'Indica si el token de acceso de la página es válido (se actualiza automáticamente)';
COMMENT ON COLUMN public.facebook_paginas.ultima_sincronizacion IS 'Última vez que se sincronizaron datos de esta página';
COMMENT ON COLUMN public.facebook_paginas.permisos_disponibles IS 'Lista de permisos disponibles para esta página';

-- Mostrar resumen de la tabla
SELECT 
    'facebook_paginas' as tabla,
    count(*) as total_registros,
    count(access_token) as con_token,
    count(*) - count(access_token) as sin_token,
    count(case when access_token_valido = true then 1 end) as tokens_validos,
    count(case when access_token_valido = false then 1 end) as tokens_invalidos
FROM public.facebook_paginas;

RAISE NOTICE 'Script completado. Tabla facebook_paginas actualizada con columnas para tokens de página.';
