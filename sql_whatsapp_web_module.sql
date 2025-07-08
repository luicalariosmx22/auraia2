-- ========================================
-- SQL para agregar el módulo WhatsApp Web
-- Ejecutar en Supabase SQL Editor
-- ========================================

-- 1. Primero, verificar la estructura de la tabla modulos_disponibles
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'modulos_disponibles' 
ORDER BY ordinal_position;

-- 2. Insertar el módulo WhatsApp Web (ajusta las columnas según tu estructura)
INSERT INTO modulos_disponibles (
    nombre, 
    icono, 
    descripcion, 
    ruta, 
    orden,
    categoria,
    requiere_permisos,
    version,
    fecha_creacion
) VALUES (
    'WhatsApp Web',
    '📱',
    'Integración con WhatsApp Web - Escanea QR y gestiona sesiones',
    'panel_cliente_whatsapp_web.whatsapp_dashboard',
    50,
    'comunicacion',
    false,
    '1.0.0',
    NOW()
) ON CONFLICT (nombre) DO UPDATE SET
    icono = EXCLUDED.icono,
    descripcion = EXCLUDED.descripcion,
    ruta = EXCLUDED.ruta,
    orden = EXCLUDED.orden,
    categoria = EXCLUDED.categoria,
    requiere_permisos = EXCLUDED.requiere_permisos,
    version = EXCLUDED.version,
    fecha_creacion = EXCLUDED.fecha_creacion;

-- 3. Activar el módulo para todas las configuraciones de bot activas
-- (Ajusta según tu estructura de datos)
UPDATE configuracion_bot 
SET modulos = CASE 
    WHEN modulos IS NULL THEN '[{"nombre": "WhatsApp Web"}]'::jsonb
    WHEN NOT modulos @> '[{"nombre": "WhatsApp Web"}]' THEN modulos || '[{"nombre": "WhatsApp Web"}]'::jsonb
    ELSE modulos
END
WHERE nombre_nora IS NOT NULL;

-- 4. Verificar que se insertó correctamente
SELECT * FROM modulos_disponibles WHERE nombre = 'WhatsApp Web';

-- 5. Verificar configuraciones de bot actualizadas
SELECT nombre_nora, modulos FROM configuracion_bot WHERE modulos @> '[{"nombre": "WhatsApp Web"}]';

-- ========================================
-- SQL alternativo si la estructura es diferente
-- ========================================

-- Si la tabla tiene columnas diferentes, usa este INSERT más simple:
/*
INSERT INTO modulos_disponibles (nombre, icono, descripcion, ruta) 
VALUES (
    'WhatsApp Web',
    '📱',
    'Integración con WhatsApp Web - Escanea QR y gestiona sesiones',
    'panel_cliente_whatsapp_web.whatsapp_dashboard'
) ON CONFLICT (nombre) DO UPDATE SET
    icono = EXCLUDED.icono,
    descripcion = EXCLUDED.descripcion,
    ruta = EXCLUDED.ruta;
*/

-- ========================================
-- Para habilitar el módulo en un bot específico
-- ========================================

-- Si quieres habilitarlo solo para un bot específico (reemplaza 'nombre_bot' por el nombre real):
/*
UPDATE configuracion_bot 
SET modulos = CASE 
    WHEN modulos IS NULL THEN '[{"nombre": "WhatsApp Web"}]'::jsonb
    WHEN NOT modulos @> '[{"nombre": "WhatsApp Web"}]' THEN modulos || '[{"nombre": "WhatsApp Web"}]'::jsonb
    ELSE modulos
END
WHERE nombre_nora = 'nombre_bot';
*/
