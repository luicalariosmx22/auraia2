-- ✅ Script completo para verificar y agregar TODAS las columnas necesarias
-- 👉 Ejecutar en Supabase SQL Editor

-- 1️⃣ AGREGAR COLUMNAS DE HORARIOS
ALTER TABLE cursos 
ADD COLUMN IF NOT EXISTS horario_lunes TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_martes TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_miercoles TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_jueves TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_viernes TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_sabado TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_domingo TEXT DEFAULT '';

-- 2️⃣ AGREGAR COLUMNAS DE UBICACIÓN
ALTER TABLE cursos 
ADD COLUMN IF NOT EXISTS direccion TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS google_maps_link TEXT DEFAULT '';

-- 3️⃣ AGREGAR COLUMNA DE PRECIO PRONTO PAGO
ALTER TABLE cursos 
ADD COLUMN IF NOT EXISTS precio_pronto_pago DECIMAL(10,2) DEFAULT 0;

-- 4️⃣ COMENTARIOS PARA DOCUMENTAR
COMMENT ON COLUMN cursos.horario_lunes IS 'Horario de clases del lunes (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_martes IS 'Horario de clases del martes (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_miercoles IS 'Horario de clases del miércoles (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_jueves IS 'Horario de clases del jueves (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_viernes IS 'Horario de clases del viernes (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_sabado IS 'Horario de clases del sábado (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_domingo IS 'Horario de clases del domingo (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.direccion IS 'Dirección física completa donde se imparte el curso presencial';
COMMENT ON COLUMN cursos.google_maps_link IS 'URL de Google Maps para ubicar fácilmente el lugar del curso';
COMMENT ON COLUMN cursos.precio_pronto_pago IS 'Precio especial para pagos realizados en las primeras 48 horas';

-- 5️⃣ VERIFICAR QUE TODAS LAS COLUMNAS EXISTEN
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'cursos' 
AND column_name IN (
    'horario_lunes', 'horario_martes', 'horario_miercoles', 'horario_jueves', 
    'horario_viernes', 'horario_sabado', 'horario_domingo',
    'direccion', 'google_maps_link', 'precio_pronto_pago'
)
ORDER BY 
    CASE column_name
        WHEN 'horario_lunes' THEN 1
        WHEN 'horario_martes' THEN 2
        WHEN 'horario_miercoles' THEN 3
        WHEN 'horario_jueves' THEN 4
        WHEN 'horario_viernes' THEN 5
        WHEN 'horario_sabado' THEN 6
        WHEN 'horario_domingo' THEN 7
        WHEN 'direccion' THEN 8
        WHEN 'google_maps_link' THEN 9
        WHEN 'precio_pronto_pago' THEN 10
        ELSE 99
    END;

-- 6️⃣ MENSAJE DE CONFIRMACIÓN
DO $$
BEGIN
    RAISE NOTICE '✅ Script ejecutado correctamente. Todas las columnas han sido agregadas.';
    RAISE NOTICE '👉 Revisa los resultados de la consulta anterior para confirmar.';
END $$;
