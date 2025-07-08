-- Tabla para subtareas completadas
CREATE TABLE IF NOT EXISTS subtareas_completadas (
    id UUID PRIMARY KEY,
    tarea_padre_id UUID,
    titulo TEXT,
    descripcion TEXT,
    prioridad TEXT,
    fecha_limite DATE,
    estatus TEXT,
    usuario_empresa_id UUID,
    empresa_id UUID,
    creado_por UUID,
    activo BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completada_en TIMESTAMP
);
