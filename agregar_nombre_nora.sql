-- Agregar campo nombre_nora a la tabla logs_webhooks_meta
ALTER TABLE public.logs_webhooks_meta 
ADD COLUMN IF NOT EXISTS nombre_nora text NULL;

-- Verificar que se agregó correctamente
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'logs_webhooks_meta' 
AND table_schema = 'public'
ORDER BY ordinal_position;
