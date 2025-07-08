-- ✅ Agregar módulo WhatsApp Web al sistema de módulos
-- Este módulo se conecta al backend de Railway para mostrar el QR y controlar la sesión

-- Insertar o actualizar el módulo WhatsApp Web
INSERT INTO modulos_disponibles (
    nombre, 
    descripcion, 
    icono, 
    ruta, 
    activo, 
    orden, 
    categoria,
    requiere_configuracion
) VALUES (
    'WhatsApp Web', 
    'Conecta y gestiona WhatsApp Web - Escanea QR para vincular tu sesión', 
    '📱', 
    'panel_cliente_whatsapp_web_bp.index', 
    true, 
    50, 
    'comunicacion',
    false
)
ON CONFLICT (nombre) DO UPDATE SET
    descripcion = EXCLUDED.descripcion,
    icono = EXCLUDED.icono,
    ruta = EXCLUDED.ruta,
    activo = EXCLUDED.activo,
    orden = EXCLUDED.orden,
    categoria = EXCLUDED.categoria,
    requiere_configuracion = EXCLUDED.requiere_configuracion;

-- Activar el módulo para todas las Noras existentes (opcional)
-- Descomenta la siguiente línea si quieres que esté activo por defecto
/*
INSERT INTO configuracion_bot (nombre_nora, modulos)
SELECT 
    nombre_nora, 
    COALESCE(modulos, '[]'::jsonb) || '[{"nombre": "WhatsApp Web", "activo": true}]'::jsonb
FROM configuracion_bot
WHERE NOT EXISTS (
    SELECT 1 FROM jsonb_array_elements(COALESCE(modulos, '[]'::jsonb)) AS elem
    WHERE elem->>'nombre' = 'WhatsApp Web'
)
ON CONFLICT (nombre_nora) DO UPDATE SET
    modulos = EXCLUDED.modulos;
*/

-- Verificar que el módulo se insertó correctamente
SELECT * FROM modulos_disponibles WHERE nombre = 'WhatsApp Web';
