-- ✅ Script SQL para agregar columna de precio de pronto pago a la tabla cursos
-- 👉 Ejecutar en Supabase SQL Editor

-- Agregar columna de precio de pronto pago
ALTER TABLE cursos 
ADD COLUMN IF NOT EXISTS precio_pronto_pago DECIMAL(10,2) DEFAULT 0;

-- Comentario para documentar la nueva columna
COMMENT ON COLUMN cursos.precio_pronto_pago IS 'Precio especial para pagos realizados en las primeras 48 horas';

-- Verificar que la columna se agregó correctamente
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'cursos' 
AND column_name = 'precio_pronto_pago';
