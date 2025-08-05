-- Script SQL para crear la tabla de configuración de notificaciones
-- Ejecuta este script en Supabase SQL Editor

CREATE TABLE IF NOT EXISTS configuracion_notificaciones (
    id SERIAL PRIMARY KEY,
    nombre_nora VARCHAR(255) NOT NULL UNIQUE,
    email_notificaciones BOOLEAN DEFAULT false,
    sms_notificaciones BOOLEAN DEFAULT false,
    email VARCHAR(255),
    telefono VARCHAR(20),
    solo_alta_prioridad BOOLEAN DEFAULT true,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_configuracion_notificaciones_nombre_nora 
ON configuracion_notificaciones(nombre_nora);

-- Función para actualizar el timestamp de actualización
CREATE OR REPLACE FUNCTION update_configuracion_notificaciones_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar automáticamente el timestamp
CREATE TRIGGER trigger_update_configuracion_notificaciones_updated_at
    BEFORE UPDATE ON configuracion_notificaciones
    FOR EACH ROW
    EXECUTE FUNCTION update_configuracion_notificaciones_updated_at();

-- Ejemplo de inserción de configuración para un usuario
-- INSERT INTO configuracion_notificaciones 
-- (nombre_nora, email_notificaciones, sms_notificaciones, email, telefono, solo_alta_prioridad)
-- VALUES 
-- ('aura_demo', true, true, 'admin@empresa.com', '+1234567890', true);

-- Comentarios sobre los campos:
-- nombre_nora: Identificador único del bot/usuario
-- email_notificaciones: Si debe enviar emails (true/false)
-- sms_notificaciones: Si debe enviar SMS (true/false) 
-- email: Dirección de correo del destinatario
-- telefono: Número de teléfono con código de país (+52, +1, etc.)
-- solo_alta_prioridad: Si solo enviar notificaciones para alertas de alta prioridad
