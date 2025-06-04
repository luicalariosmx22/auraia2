-- Tabla para comentarios de tareas
CREATE TABLE IF NOT EXISTS tarea_comentarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tarea_id UUID NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES usuarios_clientes(id) ON DELETE CASCADE,
    usuario_nombre TEXT NOT NULL,
    texto TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índice para búsquedas rápidas por tarea
CREATE INDEX IF NOT EXISTS idx_tarea_comentarios_tarea_id ON tarea_comentarios(tarea_id);
