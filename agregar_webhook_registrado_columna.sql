-- Agregar la columna webhook_registrado a meta_ads_cuentas
-- Esta columna es necesaria para el dashboard de webhooks

ALTER TABLE public.meta_ads_cuentas 
ADD COLUMN IF NOT EXISTS webhook_registrado boolean DEFAULT false;

-- Agregar también la columna actualizada_en que también necesita el código
ALTER TABLE public.meta_ads_cuentas 
ADD COLUMN IF NOT EXISTS actualizada_en timestamp without time zone DEFAULT now();

-- Crear índice para optimizar consultas por webhook_registrado
CREATE INDEX IF NOT EXISTS idx_meta_ads_cuentas_webhook 
ON public.meta_ads_cuentas(webhook_registrado);

-- Actualizar registros existentes (opcional - puedes omitir si prefieres que permanezcan en false)
-- UPDATE public.meta_ads_cuentas 
-- SET webhook_registrado = false, actualizada_en = now() 
-- WHERE webhook_registrado IS NULL;

-- Verificar que las columnas se agregaron correctamente
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'meta_ads_cuentas' 
AND column_name IN ('webhook_registrado', 'actualizada_en')
ORDER BY column_name;
