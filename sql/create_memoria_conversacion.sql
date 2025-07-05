-- Script SQL para crear tabla de memoria de conversación
-- Este script debe ejecutarse en Supabase para habilitar la memoria temporal

CREATE TABLE IF NOT EXISTS memoria_conversacion (
    id BIGSERIAL PRIMARY KEY,
    telefono TEXT NOT NULL,
    nombre_nora TEXT NOT NULL,
    datos_memoria JSONB NOT NULL,
    timestamp BIGINT NOT NULL,
    expira_en BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para búsqueda rápida
    UNIQUE(telefono, nombre_nora)
);

-- Índice para limpieza automática de registros expirados
CREATE INDEX IF NOT EXISTS idx_memoria_conversacion_expira 
ON memoria_conversacion(expira_en);

-- Índice para búsqueda por usuario
CREATE INDEX IF NOT EXISTS idx_memoria_conversacion_usuario 
ON memoria_conversacion(telefono, nombre_nora);

-- Comentarios para documentación
COMMENT ON TABLE memoria_conversacion IS 'Almacena temporalmente opciones de menú mostradas a usuarios para respuestas inteligentes';
COMMENT ON COLUMN memoria_conversacion.telefono IS 'Número de teléfono del usuario';
COMMENT ON COLUMN memoria_conversacion.nombre_nora IS 'Identificador de la instancia de Nora';
COMMENT ON COLUMN memoria_conversacion.datos_memoria IS 'Opciones mostradas al usuario en formato JSON';
COMMENT ON COLUMN memoria_conversacion.timestamp IS 'Momento de creación en timestamp Unix';
COMMENT ON COLUMN memoria_conversacion.expira_en IS 'Momento de expiración en timestamp Unix';

-- Función para limpieza automática (opcional)
-- Esta función puede ser llamada periódicamente para limpiar registros expirados
CREATE OR REPLACE FUNCTION limpiar_memoria_expirada()
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER;
BEGIN
    DELETE FROM memoria_conversacion 
    WHERE expira_en < EXTRACT(EPOCH FROM NOW());
    
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION limpiar_memoria_expirada() IS 'Elimina registros de memoria expirados y retorna la cantidad eliminada';
