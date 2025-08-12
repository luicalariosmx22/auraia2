-- Agregar columna access_token para páginas de Facebook
-- Esta columna almacenará el token de acceso específico de cada página

ALTER TABLE public.facebook_paginas 
ADD COLUMN IF NOT EXISTS access_token TEXT NULL;

-- Agregar comentario para documentación
COMMENT ON COLUMN facebook_paginas.access_token IS 'Token de acceso específico de la página de Facebook para API calls';

-- Crear índice para mejorar consultas por token (opcional, solo si se hacen consultas frecuentes)
-- CREATE INDEX IF NOT EXISTS idx_facebook_paginas_access_token ON public.facebook_paginas USING btree (access_token) TABLESPACE pg_default;

-- Verificar que la columna se agregó correctamente
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'facebook_paginas' AND column_name = 'access_token';
