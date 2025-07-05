-- ===============================================
-- SCRIPT COMPLETO PARA MÓDULO DE CURSOS - AURAAI2
-- COMPATIBLE CON POSTGRESQL/SUPABASE
-- ===============================================

-- 1. Crear tipos enum
DO $$ BEGIN
    CREATE TYPE estado_inscripcion_enum AS ENUM ('activa', 'completada', 'cancelada', 'suspendida');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE estado_pago_enum AS ENUM ('pendiente', 'completado', 'fallido', 'reembolsado');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Tabla principal de cursos
CREATE TABLE IF NOT EXISTS cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    contenido_detalle TEXT,
    objetivos TEXT,
    requisitos TEXT,
    categoria VARCHAR(100),
    nivel VARCHAR(50),
    modalidad VARCHAR(50),
    precio DECIMAL(10,2) DEFAULT 0,
    precio_pronto_pago DECIMAL(10,2) DEFAULT 0,
    duracion_horas INTEGER DEFAULT 0,
    instructor VARCHAR(255),
    direccion TEXT,
    google_maps_link TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN DEFAULT true,
    estudiantes_inscritos INTEGER DEFAULT 0,
    max_estudiantes INTEGER DEFAULT 999,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Horarios por día de la semana
    horario_lunes VARCHAR(100),
    horario_martes VARCHAR(100),
    horario_miercoles VARCHAR(100),
    horario_jueves VARCHAR(100),
    horario_viernes VARCHAR(100),
    horario_sabado VARCHAR(100),
    horario_domingo VARCHAR(100)
);

-- Índices para tabla cursos
CREATE INDEX IF NOT EXISTS idx_cursos_nora ON cursos (nombre_nora);
CREATE INDEX IF NOT EXISTS idx_cursos_activo ON cursos (activo);
CREATE INDEX IF NOT EXISTS idx_cursos_categoria ON cursos (categoria);
CREATE INDEX IF NOT EXISTS idx_cursos_nivel ON cursos (nivel);
CREATE INDEX IF NOT EXISTS idx_cursos_modalidad ON cursos (modalidad);

-- 3. Tabla de estudiantes de cursos
CREATE TABLE IF NOT EXISTS estudiantes_cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    profesion_ocupacion VARCHAR(255),
    edad INTEGER,
    direccion TEXT,
    fecha_nacimiento DATE,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Constraint único por email y nora
    CONSTRAINT unique_email_nora UNIQUE (email, nombre_nora)
);

-- Índices para tabla estudiantes_cursos
CREATE INDEX IF NOT EXISTS idx_estudiantes_nora ON estudiantes_cursos (nombre_nora);
CREATE INDEX IF NOT EXISTS idx_estudiantes_email ON estudiantes_cursos (email);
CREATE INDEX IF NOT EXISTS idx_estudiantes_activo ON estudiantes_cursos (activo);

-- 4. Tabla de inscripciones (relación entre cursos y estudiantes)
CREATE TABLE IF NOT EXISTS inscripciones_cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    curso_id UUID NOT NULL,
    estudiante_id UUID NOT NULL,
    estado_inscripcion estado_inscripcion_enum DEFAULT 'activa',
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_completacion TIMESTAMP NULL,
    fecha_cancelacion TIMESTAMP NULL,
    motivo_cancelacion TEXT,
    calificacion_final DECIMAL(5,2),
    comentarios TEXT,
    metodo_pago VARCHAR(50),
    monto_pagado DECIMAL(10,2) DEFAULT 0,
    fecha_pago TIMESTAMP NULL,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Relaciones
    CONSTRAINT fk_inscripciones_curso FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
    CONSTRAINT fk_inscripciones_estudiante FOREIGN KEY (estudiante_id) REFERENCES estudiantes_cursos(id) ON DELETE CASCADE,
    
    -- Constraint único para evitar doble inscripción
    CONSTRAINT unique_curso_estudiante UNIQUE (curso_id, estudiante_id)
);

-- Índices para tabla inscripciones_cursos
CREATE INDEX IF NOT EXISTS idx_inscripciones_curso ON inscripciones_cursos (curso_id);
CREATE INDEX IF NOT EXISTS idx_inscripciones_estudiante ON inscripciones_cursos (estudiante_id);
CREATE INDEX IF NOT EXISTS idx_inscripciones_estado ON inscripciones_cursos (estado_inscripcion);
CREATE INDEX IF NOT EXISTS idx_inscripciones_nora ON inscripciones_cursos (nombre_nora);
CREATE INDEX IF NOT EXISTS idx_inscripciones_fecha ON inscripciones_cursos (fecha_inscripcion);

-- 5. Tabla de categorías de cursos (opcional, para normalización)
CREATE TABLE IF NOT EXISTS categorias_cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    orden_display INTEGER DEFAULT 0,
    color_hex VARCHAR(7) DEFAULT '#3B82F6',
    icono VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Constraint único por nombre y nora
    CONSTRAINT unique_categoria_nora UNIQUE (nombre, nombre_nora)
);

-- Índices para tabla categorias_cursos
CREATE INDEX IF NOT EXISTS idx_categorias_nora ON categorias_cursos (nombre_nora);
CREATE INDEX IF NOT EXISTS idx_categorias_activo ON categorias_cursos (activo);
CREATE INDEX IF NOT EXISTS idx_categorias_orden ON categorias_cursos (orden_display);

-- 6. Tabla de niveles de cursos (opcional, para normalización)
CREATE TABLE IF NOT EXISTS niveles_cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    orden_dificultad INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Constraint único por nombre y nora
    CONSTRAINT unique_nivel_nora UNIQUE (nombre, nombre_nora)
);

-- Índices para tabla niveles_cursos
CREATE INDEX IF NOT EXISTS idx_niveles_nora ON niveles_cursos (nombre_nora);
CREATE INDEX IF NOT EXISTS idx_niveles_activo ON niveles_cursos (activo);
CREATE INDEX IF NOT EXISTS idx_niveles_orden ON niveles_cursos (orden_dificultad);

-- 7. Tabla de asistencias (opcional, para control detallado)
CREATE TABLE IF NOT EXISTS asistencias_cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inscripcion_id UUID NOT NULL,
    fecha_clase DATE NOT NULL,
    asistio BOOLEAN DEFAULT false,
    hora_llegada TIME NULL,
    hora_salida TIME NULL,
    comentarios TEXT,
    justificacion TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Relaciones
    CONSTRAINT fk_asistencias_inscripcion FOREIGN KEY (inscripcion_id) REFERENCES inscripciones_cursos(id) ON DELETE CASCADE,
    
    -- Constraint único para evitar doble registro
    CONSTRAINT unique_asistencia_fecha UNIQUE (inscripcion_id, fecha_clase)
);

-- Índices para tabla asistencias_cursos
CREATE INDEX IF NOT EXISTS idx_asistencias_inscripcion ON asistencias_cursos (inscripcion_id);
CREATE INDEX IF NOT EXISTS idx_asistencias_fecha ON asistencias_cursos (fecha_clase);
CREATE INDEX IF NOT EXISTS idx_asistencias_nora ON asistencias_cursos (nombre_nora);

-- 8. Tabla de pagos de cursos (opcional, para control financiero)
CREATE TABLE IF NOT EXISTS pagos_cursos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inscripcion_id UUID NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL,
    estado_pago estado_pago_enum DEFAULT 'pendiente',
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    referencia_pago VARCHAR(255),
    comprobante_url TEXT,
    comentarios TEXT,
    nombre_nora VARCHAR(100) NOT NULL,
    
    -- Relaciones
    CONSTRAINT fk_pagos_inscripcion FOREIGN KEY (inscripcion_id) REFERENCES inscripciones_cursos(id) ON DELETE CASCADE
);

-- Índices para tabla pagos_cursos
CREATE INDEX IF NOT EXISTS idx_pagos_inscripcion ON pagos_cursos (inscripcion_id);
CREATE INDEX IF NOT EXISTS idx_pagos_estado ON pagos_cursos (estado_pago);
CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos_cursos (fecha_pago);
CREATE INDEX IF NOT EXISTS idx_pagos_nora ON pagos_cursos (nombre_nora);
CREATE INDEX IF NOT EXISTS idx_pagos_metodo ON pagos_cursos (metodo_pago);

-- ===============================================
-- FUNCIONES Y TRIGGERS PARA POSTGRESQL
-- ===============================================

-- Función para actualizar contador de estudiantes inscritos
CREATE OR REPLACE FUNCTION actualizar_contador_estudiantes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE cursos 
        SET estudiantes_inscritos = (
            SELECT COUNT(*) 
            FROM inscripciones_cursos 
            WHERE curso_id = OLD.curso_id 
            AND estado_inscripcion IN ('activa', 'completada')
        )
        WHERE id = OLD.curso_id;
        RETURN OLD;
    ELSE
        UPDATE cursos 
        SET estudiantes_inscritos = (
            SELECT COUNT(*) 
            FROM inscripciones_cursos 
            WHERE curso_id = NEW.curso_id 
            AND estado_inscripcion IN ('activa', 'completada')
        )
        WHERE id = NEW.curso_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar contador de estudiantes
DROP TRIGGER IF EXISTS trigger_actualizar_estudiantes_insert ON inscripciones_cursos;
CREATE TRIGGER trigger_actualizar_estudiantes_insert
    AFTER INSERT ON inscripciones_cursos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_contador_estudiantes();

DROP TRIGGER IF EXISTS trigger_actualizar_estudiantes_update ON inscripciones_cursos;
CREATE TRIGGER trigger_actualizar_estudiantes_update
    AFTER UPDATE ON inscripciones_cursos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_contador_estudiantes();

DROP TRIGGER IF EXISTS trigger_actualizar_estudiantes_delete ON inscripciones_cursos;
CREATE TRIGGER trigger_actualizar_estudiantes_delete
    AFTER DELETE ON inscripciones_cursos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_contador_estudiantes();

-- Triggers para actualizar timestamp
DROP TRIGGER IF EXISTS trigger_update_cursos_timestamp ON cursos;
CREATE TRIGGER trigger_update_cursos_timestamp
    BEFORE UPDATE ON cursos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trigger_update_estudiantes_timestamp ON estudiantes_cursos;
CREATE TRIGGER trigger_update_estudiantes_timestamp
    BEFORE UPDATE ON estudiantes_cursos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

-- ===============================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ===============================================

-- Insertar categorías predeterminadas
INSERT INTO categorias_cursos (nombre, descripcion, color_hex, icono, nombre_nora) 
VALUES 
('Tecnología', 'Cursos relacionados con programación y tecnología', '#3B82F6', '💻', 'aura'),
('Marketing', 'Cursos de marketing digital y tradicional', '#10B981', '📈', 'aura'),
('Diseño', 'Cursos de diseño gráfico y UX/UI', '#8B5CF6', '🎨', 'aura'),
('Negocios', 'Cursos de administración y emprendimiento', '#F59E0B', '💼', 'aura'),
('Idiomas', 'Cursos de idiomas y comunicación', '#EF4444', '🗣️', 'aura'),
('Arte', 'Cursos de arte y creatividad', '#EC4899', '🎭', 'aura')
ON CONFLICT (nombre, nombre_nora) DO NOTHING;

-- Insertar niveles predeterminados
INSERT INTO niveles_cursos (nombre, descripcion, orden_dificultad, nombre_nora) 
VALUES 
('Principiante', 'Nivel básico, sin conocimientos previos requeridos', 1, 'aura'),
('Intermedio', 'Nivel medio, requiere conocimientos básicos', 2, 'aura'),
('Avanzado', 'Nivel alto, requiere experiencia previa', 3, 'aura'),
('Experto', 'Nivel profesional, para especialistas', 4, 'aura')
ON CONFLICT (nombre, nombre_nora) DO NOTHING;

-- ===============================================
-- VISTAS ÚTILES (OPCIONAL)
-- ===============================================

-- Vista para obtener información completa de inscripciones
CREATE OR REPLACE VIEW vista_inscripciones_completa AS
SELECT 
    i.id as inscripcion_id,
    i.estado_inscripcion,
    i.fecha_inscripcion,
    i.fecha_completacion,
    i.calificacion_final,
    i.monto_pagado,
    c.id as curso_id,
    c.titulo as curso_titulo,
    c.categoria as curso_categoria,
    c.precio as curso_precio,
    c.modalidad as curso_modalidad,
    e.id as estudiante_id,
    e.nombre_completo as estudiante_nombre,
    e.email as estudiante_email,
    e.telefono as estudiante_telefono,
    e.profesion_ocupacion as estudiante_profesion,
    i.nombre_nora
FROM inscripciones_cursos i
JOIN cursos c ON i.curso_id = c.id
JOIN estudiantes_cursos e ON i.estudiante_id = e.id;

-- Vista para estadísticas de cursos
CREATE OR REPLACE VIEW vista_estadisticas_cursos AS
SELECT 
    c.id,
    c.titulo,
    c.categoria,
    c.precio,
    c.estudiantes_inscritos,
    (c.precio * c.estudiantes_inscritos) as ingresos_totales,
    COUNT(CASE WHEN i.estado_inscripcion = 'activa' THEN 1 END) as inscritos_activos,
    COUNT(CASE WHEN i.estado_inscripcion = 'completada' THEN 1 END) as completados,
    COUNT(CASE WHEN i.estado_inscripcion = 'cancelada' THEN 1 END) as cancelados,
    AVG(i.calificacion_final) as calificacion_promedio,
    c.nombre_nora
FROM cursos c
LEFT JOIN inscripciones_cursos i ON c.id = i.curso_id
GROUP BY c.id, c.titulo, c.categoria, c.precio, c.estudiantes_inscritos, c.nombre_nora;

-- ===============================================
-- ÍNDICES ADICIONALES PARA RENDIMIENTO
-- ===============================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_inscripciones_curso_estado ON inscripciones_cursos(curso_id, estado_inscripcion);
CREATE INDEX IF NOT EXISTS idx_inscripciones_estudiante_estado ON inscripciones_cursos(estudiante_id, estado_inscripcion);
CREATE INDEX IF NOT EXISTS idx_cursos_activo_nora ON cursos(activo, nombre_nora);
CREATE INDEX IF NOT EXISTS idx_estudiantes_activo_nora ON estudiantes_cursos(activo, nombre_nora);

-- ===============================================
-- RLS (ROW LEVEL SECURITY) PARA SUPABASE
-- ===============================================

-- Habilitar RLS en todas las tablas
ALTER TABLE cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE estudiantes_cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE inscripciones_cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias_cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE niveles_cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE asistencias_cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagos_cursos ENABLE ROW LEVEL SECURITY;

-- Políticas básicas de RLS (ajustar según necesidades)
-- Estas políticas permiten acceso completo - personalizar según requerimientos de seguridad

CREATE POLICY "Enable all access for authenticated users" ON cursos
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON estudiantes_cursos
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON inscripciones_cursos
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON categorias_cursos
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON niveles_cursos
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON asistencias_cursos
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON pagos_cursos
    FOR ALL USING (auth.role() = 'authenticated');

-- ===============================================
-- COMENTARIOS FINALES
-- ===============================================

/*
NOTAS IMPORTANTES PARA SUPABASE:

1. Este script está 100% adaptado para PostgreSQL/Supabase
2. Usa UUIDs para claves primarias (compatible con Supabase por defecto)
3. Usa funciones y triggers nativos de PostgreSQL
4. Incluye RLS (Row Level Security) habilitado
5. Usa ON CONFLICT en lugar de IGNORE para inserts
6. Los índices están optimizados para PostgreSQL

CÓMO USAR EN SUPABASE:
1. Ve al SQL Editor en tu dashboard de Supabase
2. Pega y ejecuta este script completo
3. Todas las tablas, funciones, triggers y políticas se crearán automáticamente

PERSONALIZACIÓN:
- Ajusta las políticas de RLS según tus necesidades de seguridad
- Modifica los ENUMs si necesitas otros estados
- Agrega más categorías y niveles predeterminados si es necesario
- Los triggers mantienen automáticamente los contadores actualizados

SEGURIDAD:
- RLS está habilitado en todas las tablas
- Las políticas actuales permiten acceso a usuarios autenticados
- Personaliza las políticas según tu lógica de negocio

CLAVES PRIMARIAS:
- Todas las tablas usan UUIDs para máxima compatibilidad con Supabase
- gen_random_uuid() genera automáticamente IDs únicos

*/
