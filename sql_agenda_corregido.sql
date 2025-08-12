-- ================================================
-- 📅 SQL CORREGIDO PARA MÓDULO DE AGENDA - Ejecutar en Supabase
-- ================================================
-- SOLUCIÓN: Las tablas existen pero les faltan columnas y tienen problemas de RLS

-- 1️⃣ AGREGAR COLUMNAS FALTANTES A agenda_eventos
-- ================================================
DO $$
BEGIN
    -- Agregar columna 'tipo' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'tipo') THEN
        ALTER TABLE agenda_eventos ADD COLUMN tipo VARCHAR(50) DEFAULT 'reunion';
    END IF;
    
    -- Agregar columna 'empresa_id' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'empresa_id') THEN
        ALTER TABLE agenda_eventos ADD COLUMN empresa_id BIGINT;
    END IF;
    
    -- Agregar columna 'tarea_id' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'tarea_id') THEN
        ALTER TABLE agenda_eventos ADD COLUMN tarea_id BIGINT;
    END IF;
    
    -- Agregar columna 'google_event_id' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'google_event_id') THEN
        ALTER TABLE agenda_eventos ADD COLUMN google_event_id VARCHAR(100);
    END IF;
    
    -- Agregar columna 'todo_el_dia' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'todo_el_dia') THEN
        ALTER TABLE agenda_eventos ADD COLUMN todo_el_dia BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Agregar columna 'recordatorio_minutos' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'recordatorio_minutos') THEN
        ALTER TABLE agenda_eventos ADD COLUMN recordatorio_minutos INTEGER DEFAULT 15;
    END IF;
    
    -- Agregar columna 'estado' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'estado') THEN
        ALTER TABLE agenda_eventos ADD COLUMN estado VARCHAR(20) DEFAULT 'confirmado';
    END IF;
    
    -- Agregar columna 'color' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'color') THEN
        ALTER TABLE agenda_eventos ADD COLUMN color VARCHAR(7) DEFAULT '#3b82f6';
    END IF;
    
    -- Agregar columna 'creado_por' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'creado_por') THEN
        ALTER TABLE agenda_eventos ADD COLUMN creado_por VARCHAR(100);
    END IF;
    
    -- Agregar columna 'ubicacion' si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'ubicacion') THEN
        ALTER TABLE agenda_eventos ADD COLUMN ubicacion VARCHAR(300);
    END IF;
END $$;

-- 2️⃣ CREAR TABLA google_calendar_sync SI NO EXISTE
-- ================================================
CREATE TABLE IF NOT EXISTS google_calendar_sync (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL UNIQUE,
    google_client_id VARCHAR(200),
    google_client_secret VARCHAR(200),
    google_access_token TEXT,
    google_refresh_token TEXT,
    google_calendar_id VARCHAR(200),
    token_expires_at TIMESTAMPTZ,
    sync_activo BOOLEAN DEFAULT FALSE,
    ultima_sincronizacion TIMESTAMPTZ,
    configurado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);

-- 3️⃣ CREAR ÍNDICES SEGUROS (solo si no existen)
-- ================================================
DO $$
BEGIN
    -- Índices para agenda_eventos
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agenda_eventos_nombre_nora') THEN
        CREATE INDEX idx_agenda_eventos_nombre_nora ON agenda_eventos(nombre_nora);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agenda_eventos_fecha_inicio') THEN
        CREATE INDEX idx_agenda_eventos_fecha_inicio ON agenda_eventos(fecha_inicio);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agenda_eventos_fecha_fin') THEN
        CREATE INDEX idx_agenda_eventos_fecha_fin ON agenda_eventos(fecha_fin);
    END IF;
    
    -- Solo crear índice de 'tipo' si la columna existe
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'tipo') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agenda_eventos_tipo') THEN
            CREATE INDEX idx_agenda_eventos_tipo ON agenda_eventos(tipo);
        END IF;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'empresa_id') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agenda_eventos_empresa_id') THEN
            CREATE INDEX idx_agenda_eventos_empresa_id ON agenda_eventos(empresa_id);
        END IF;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'agenda_eventos' AND column_name = 'tarea_id') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agenda_eventos_tarea_id') THEN
            CREATE INDEX idx_agenda_eventos_tarea_id ON agenda_eventos(tarea_id);
        END IF;
    END IF;
    
    -- Índices para google_calendar_sync
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_google_calendar_sync_nombre_nora') THEN
        CREATE INDEX idx_google_calendar_sync_nombre_nora ON google_calendar_sync(nombre_nora);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_google_calendar_sync_activo') THEN
        CREATE INDEX idx_google_calendar_sync_activo ON google_calendar_sync(sync_activo);
    END IF;
END $$;

-- 4️⃣ CONFIGURAR RLS CORRECTAMENTE
-- ================================================
-- Habilitar RLS
ALTER TABLE agenda_eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_calendar_sync ENABLE ROW LEVEL SECURITY;

-- Eliminar políticas existentes si existen
DROP POLICY IF EXISTS "agenda_eventos_policy" ON agenda_eventos;
DROP POLICY IF EXISTS "google_calendar_sync_policy" ON google_calendar_sync;

-- Crear políticas permisivas (permitir todo por ahora)
CREATE POLICY "agenda_eventos_policy" ON agenda_eventos
    FOR ALL 
    USING (true)
    WITH CHECK (true);

CREATE POLICY "google_calendar_sync_policy" ON google_calendar_sync
    FOR ALL 
    USING (true)
    WITH CHECK (true);

-- 5️⃣ REGISTRAR MÓDULO EN SISTEMA (seguro)
-- ================================================
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta)
SELECT 'agenda', 'Sistema de gestión de eventos y calendario con sincronización Google Calendar', '📅', 'panel_cliente_agenda.panel_cliente_agenda_bp'
WHERE NOT EXISTS (
    SELECT 1 FROM modulos_disponibles WHERE nombre = 'agenda'
);

-- 6️⃣ ACTIVAR MÓDULO PARA AURA
-- ================================================
UPDATE configuracion_bot 
SET modulos = jsonb_set(
    COALESCE(modulos, '{}'), 
    '{agenda}', 
    'true'
)
WHERE nombre_nora = 'aura';

-- 7️⃣ CONFIGURACIÓN INICIAL GOOGLE CALENDAR
-- ================================================
INSERT INTO google_calendar_sync (nombre_nora, sync_activo)
SELECT 'aura', FALSE
WHERE NOT EXISTS (
    SELECT 1 FROM google_calendar_sync WHERE nombre_nora = 'aura'
);

-- 8️⃣ INSERTAR EVENTOS DE EJEMPLO (seguro)
-- ================================================
DO $$
BEGIN
    -- Solo insertar si no hay eventos para aura
    IF NOT EXISTS (SELECT 1 FROM agenda_eventos WHERE nombre_nora = 'aura') THEN
        INSERT INTO agenda_eventos (
            nombre_nora, titulo, descripcion, fecha_inicio, fecha_fin, 
            tipo, ubicacion, color, estado
        ) VALUES 
        (
            'aura',
            'Reunión de planificación',
            'Reunión mensual para revisar objetivos y estrategias',
            NOW() + INTERVAL '1 day',
            NOW() + INTERVAL '1 day' + INTERVAL '1 hour',
            'reunion',
            'Sala de juntas principal',
            '#3b82f6',
            'confirmado'
        ),
        (
            'aura',
            'Llamada con cliente',
            'Seguimiento proyecto desarrollo web',
            NOW() + INTERVAL '2 days',
            NOW() + INTERVAL '2 days' + INTERVAL '30 minutes',
            'llamada',
            'Videoconferencia',
            '#10b981',
            'confirmado'
        ),
        (
            'aura',
            'Presentación propuesta',
            'Presentar nueva propuesta de marketing digital',
            NOW() + INTERVAL '3 days',
            NOW() + INTERVAL '3 days' + INTERVAL '1.5 hours',
            'cita',
            'Oficina del cliente',
            '#f59e0b',
            'tentativo'
        );
    END IF;
END $$;

-- ================================================
-- ✅ VERIFICACIONES FINALES
-- ================================================

-- Verificar columnas de agenda_eventos
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'agenda_eventos' 
ORDER BY ordinal_position;

-- Verificar que el módulo se registró
SELECT nombre, descripcion, icono 
FROM modulos_disponibles 
WHERE nombre = 'agenda';

-- Verificar que el módulo se activó para aura
SELECT nombre_nora, modulos->'agenda' as agenda_activo
FROM configuracion_bot 
WHERE nombre_nora = 'aura';

-- Verificar configuración Google Calendar
SELECT nombre_nora, sync_activo, configurado_en
FROM google_calendar_sync 
WHERE nombre_nora = 'aura';

-- Contar eventos para aura
SELECT COUNT(*) as total_eventos
FROM agenda_eventos 
WHERE nombre_nora = 'aura';

-- ================================================
-- 📋 RESUMEN DE CAMBIOS APLICADOS:
-- 
-- ✅ Columnas agregadas a agenda_eventos:
--    - tipo, empresa_id, tarea_id, google_event_id
--    - todo_el_dia, recordatorio_minutos, estado
--    - color, creado_por, ubicacion
--
-- ✅ Tabla google_calendar_sync creada
-- ✅ Índices optimizados agregados
-- ✅ RLS configurado correctamente
-- ✅ Políticas permisivas aplicadas
-- ✅ Módulo registrado y activado
-- ✅ Configuración Google Calendar inicializada
-- ✅ Eventos de ejemplo agregados (si no existían)
-- ================================================
