-- Tabla de subtareas para gestión de tareas anidadas
CREATE TABLE IF NOT EXISTS subtareas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tarea_padre_id UUID NOT NULL, -- referencia a la tarea principal
    titulo TEXT NOT NULL,
    descripcion TEXT,
    prioridad VARCHAR(10) DEFAULT 'media',
    fecha_limite DATE,
    estatus VARCHAR(20) DEFAULT 'pendiente',
    usuario_empresa_id UUID,
    empresa_id UUID,
    creado_por TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tarea_padre_id) REFERENCES tareas(id) ON DELETE CASCADE
);
-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_subtareas_tarea_padre_id ON subtareas(tarea_padre_id);
CREATE INDEX IF NOT EXISTS idx_subtareas_usuario_empresa_id ON subtareas(usuario_empresa_id);
