-- Actualizar nombre_nora a 'aura' para todos los registros
UPDATE public.meta_ads_cuentas 
SET nombre_nora = 'aura' 
WHERE nombre_nora IS NULL OR nombre_nora != 'aura';

-- Verificar los cambios
SELECT 
    COUNT(*) as total_registros,
    COUNT(CASE WHEN nombre_nora = 'aura' THEN 1 END) as con_nombre_nora_aura,
    COUNT(CASE WHEN nombre_nora IS NULL THEN 1 END) as con_nombre_nora_null
FROM public.meta_ads_cuentas;

-- Mostrar algunos registros para verificar
SELECT 
    id_cuenta_publicitaria,
    nombre_cliente,
    nombre_nora,
    tipo_plataforma,
    account_status
FROM public.meta_ads_cuentas 
LIMIT 10;
