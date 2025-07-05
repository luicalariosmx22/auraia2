-- Script para añadir columnas adicionales a la tabla google_ads_palabras_clave
-- Añade campos para relacionar directamente la keyword con la cuenta de Google Ads

-- Añadir columna customer_id (ID de cliente de Google Ads)
ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS customer_id text NULL;

-- Añadir columna nombre_cuenta (Nombre descriptivo de la cuenta)
ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS nombre_cuenta text NULL;

-- Añadir columnas para métricas adicionales
-- Estas ya existen como texto pero las añadimos como columnas numéricas para mejor análisis
ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS impresiones_num bigint NULL;

ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS clics_num bigint NULL;

ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS ctr_num numeric(10,2) NULL;

ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS cpc_promedio_num numeric(10,2) NULL;

ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS costo_num numeric(10,2) NULL;

ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS conversiones_num numeric(10,2) NULL;

-- Añadir columnas completamente nuevas
ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS conversion_value numeric(12,2) NULL;

ALTER TABLE public.google_ads_palabras_clave 
ADD COLUMN IF NOT EXISTS conversion_rate numeric(10,2) NULL;

-- Crear índices para mejorar las búsquedas
CREATE INDEX IF NOT EXISTS idx_palabras_clave_customer_id
ON public.google_ads_palabras_clave (customer_id);

CREATE INDEX IF NOT EXISTS idx_palabras_clave_impresiones
ON public.google_ads_palabras_clave (impresiones_num);

CREATE INDEX IF NOT EXISTS idx_palabras_clave_clics
ON public.google_ads_palabras_clave (clics_num);

CREATE INDEX IF NOT EXISTS idx_palabras_clave_conversiones
ON public.google_ads_palabras_clave (conversiones_num);

-- Comentario para las nuevas columnas
COMMENT ON COLUMN public.google_ads_palabras_clave.customer_id IS 'ID de cliente de Google Ads';
COMMENT ON COLUMN public.google_ads_palabras_clave.nombre_cuenta IS 'Nombre descriptivo de la cuenta de Google Ads';
COMMENT ON COLUMN public.google_ads_palabras_clave.impresiones_num IS 'Impresiones totales (numérico)';
COMMENT ON COLUMN public.google_ads_palabras_clave.clics_num IS 'Clics recibidos (numérico)';
COMMENT ON COLUMN public.google_ads_palabras_clave.ctr_num IS 'Click Through Rate (CTR) en porcentaje';
COMMENT ON COLUMN public.google_ads_palabras_clave.cpc_promedio_num IS 'Costo promedio por clic';
COMMENT ON COLUMN public.google_ads_palabras_clave.costo_num IS 'Costo total';
COMMENT ON COLUMN public.google_ads_palabras_clave.conversiones_num IS 'Número de conversiones (numérico)';
COMMENT ON COLUMN public.google_ads_palabras_clave.conversion_value IS 'Valor total de conversiones';
COMMENT ON COLUMN public.google_ads_palabras_clave.conversion_rate IS 'Porcentaje de conversión';

-- Actualizar el mapeo de campos válidos en el script actualizar_google_ads_cuentas.py:
-- campos_validos = [
--     'estado_palabra_clave', 'palabra_clave', 'tipo_concordancia',
--     'campaña', 'grupo_anuncios', 'estado', 'motivos_estado',
--     'url_final', 'url_final_movil', 'impresiones', 'ctr',
--     'codigo_moneda', 'costo', 'clics', 'porcentaje_conversion',
--     'conversiones', 'cpc_promedio', 'costo_por_conversion',
--     'id_grupo_anuncios', 'id_campaña', 'id_palabra_clave',
--     'nombre_nora', 'empresa_id', 'customer_id', 'nombre_cuenta',
--     'impresiones_num', 'clics_num', 'ctr_num', 'cpc_promedio_num', 
--     'costo_num', 'conversiones_num', 'conversion_value', 'conversion_rate'
-- ]
