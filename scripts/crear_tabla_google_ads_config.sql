-- Crear tabla para configuración de Google Ads
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS google_ads_config (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID,
    cliente_id VARCHAR,
    developer_token VARCHAR,
    developer_token_valid BOOLEAN DEFAULT FALSE,
    client_id VARCHAR,
    client_secret VARCHAR,
    login_customer_id VARCHAR,
    refresh_token VARCHAR,
    refresh_token_valid BOOLEAN DEFAULT FALSE,
    access_token VARCHAR,
    token_type VARCHAR DEFAULT 'Bearer',
    expires_in INTEGER DEFAULT 3600,
    activo BOOLEAN DEFAULT TRUE
);

-- Crear o reemplazar la función para actualizar el timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear o reemplazar el trigger para actualizar 'updated_at' automáticamente
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON google_ads_config
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Insertar una entrada de prueba para verificar que la tabla funciona
-- Descomentar si es necesario
/*
INSERT INTO google_ads_config (
    client_id,
    client_secret,
    developer_token,
    developer_token_valid,
    login_customer_id
) VALUES (
    'ejemplo-client-id.apps.googleusercontent.com',
    'ejemplo-client-secret',
    'ejemplo-developer-token',
    TRUE,
    '1234567890'
);
*/

-- Comentario con instrucciones
COMMENT ON TABLE google_ads_config IS 'Tabla para almacenar la configuración y tokens de acceso para la API de Google Ads';
