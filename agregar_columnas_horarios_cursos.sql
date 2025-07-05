-- ✅ Script SQL para agregar columnas de horarios por día a la tabla cursos
-- 👉 Ejecutar en Supabase SQL Editor

-- Agregar columnas de horarios para cada día de la semana
ALTER TABLE cursos 
ADD COLUMN IF NOT EXISTS horario_lunes TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_martes TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_miercoles TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_jueves TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_viernes TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_sabado TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS horario_domingo TEXT DEFAULT '';

-- Comentarios para documentar las nuevas columnas
COMMENT ON COLUMN cursos.horario_lunes IS 'Horario de clases del lunes (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_martes IS 'Horario de clases del martes (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_miercoles IS 'Horario de clases del miércoles (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_jueves IS 'Horario de clases del jueves (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_viernes IS 'Horario de clases del viernes (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_sabado IS 'Horario de clases del sábado (formato: HH:MM - HH:MM)';
COMMENT ON COLUMN cursos.horario_domingo IS 'Horario de clases del domingo (formato: HH:MM - HH:MM)';

-- Verificar que las columnas se agregaron correctamente
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'cursos' 
AND column_name LIKE 'horario_%'
ORDER BY column_name;
