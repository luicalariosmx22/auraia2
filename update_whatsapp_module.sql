-- Actualizar el módulo de WhatsApp Web para usar la nueva integración
UPDATE "public"."modulos_disponibles" 
SET 
    "nombre" = 'WhatsApp Web',
    "descripcion" = 'Conecta con WhatsApp Web usando Railway - Escanea QR para vincular',
    "icono" = '📱',
    "ruta" = 'panel_cliente_whatsapp_web_bp.index'
WHERE "id" = 'd155d3f7-183f-4ccb-ba1c-795964433058';

-- Verificar que se actualizó correctamente
SELECT * FROM "public"."modulos_disponibles" WHERE "id" = 'd155d3f7-183f-4ccb-ba1c-795964433058';
