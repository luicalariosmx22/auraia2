-- ========================================
-- SQL para verificar y preparar la integración
-- ========================================

-- 1. Ver la estructura actual de modulos_disponibles
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'modulos_disponibles' 
ORDER BY ordinal_position;

-- 2. Ver todos los módulos existentes
SELECT * FROM modulos_disponibles ORDER BY nombre;

-- 3. Ver configuraciones de bot actuales
SELECT nombre_nora, modulos FROM configuracion_bot LIMIT 5;

-- 4. Verificar si ya existe el módulo WhatsApp Web
SELECT * FROM modulos_disponibles WHERE nombre ILIKE '%whatsapp%';

-- 5. Ver la estructura de configuracion_bot
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'configuracion_bot' 
ORDER BY ordinal_position;

-- ========================================
-- Si necesitas crear las tablas desde cero
-- ========================================

-- Crear tabla modulos_disponibles (solo si no existe)
CREATE TABLE IF NOT EXISTS modulos_disponibles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    icono VARCHAR(10),
    descripcion TEXT,
    ruta VARCHAR(200),
    orden INTEGER DEFAULT 0,
    categoria VARCHAR(50),
    activo BOOLEAN DEFAULT true,
    requiere_permisos BOOLEAN DEFAULT false,
    version VARCHAR(20) DEFAULT '1.0.0',
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_modulos_disponibles_nombre ON modulos_disponibles(nombre);
CREATE INDEX IF NOT EXISTS idx_modulos_disponibles_activo ON modulos_disponibles(activo);
CREATE INDEX IF NOT EXISTS idx_modulos_disponibles_categoria ON modulos_disponibles(categoria);
