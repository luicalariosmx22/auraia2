-- ========================================
-- SQL para ACTUALIZAR el módulo WhatsApp Web existente
-- ========================================

-- Actualizar la ruta del módulo existente qr_whatsapp_web
UPDATE modulos_disponibles 
SET ruta = 'panel_cliente_whatsapp_web.whatsapp_dashboard'
WHERE nombre = 'qr_whatsapp_web';

-- Verificar que se actualizó correctamente
SELECT nombre, descripcion, icono, ruta 
FROM modulos_disponibles 
WHERE nombre = 'qr_whatsapp_web';

-- ========================================
-- Verificar configuraciones de bot que usan este módulo
-- ========================================

-- Ver qué bots tienen el módulo qr_whatsapp_web habilitado
SELECT nombre_nora, modulos 
FROM configuracion_bot 
WHERE modulos::text ILIKE '%qr_whatsapp_web%';

-- Si no hay ningún bot con el módulo, habilitarlo para todos los bots activos
-- (descomenta la siguiente línea si es necesario)
/*
UPDATE configuracion_bot 
SET modulos = CASE 
    WHEN modulos IS NULL THEN '[{"nombre": "qr_whatsapp_web"}]'::jsonb
    WHEN NOT modulos @> '[{"nombre": "qr_whatsapp_web"}]' THEN modulos || '[{"nombre": "qr_whatsapp_web"}]'::jsonb
    ELSE modulos
END
WHERE nombre_nora IS NOT NULL;
*/
