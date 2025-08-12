-- ================================================
-- 📅 SQL PARA MÓDULO DE AGENDA - Ejecutar en Supabase
-- ================================================

-- 1️⃣ CREAR TABLA PRINCIPAL DE EVENTOS
-- ================================================
CREATE TABLE IF NOT EXISTS agenda_eventos (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ,
    ubicacion VARCHAR(300),
    tipo VARCHAR(50) DEFAULT 'reunion',
    empresa_id BIGINT,
    tarea_id BIGINT,
    google_event_id VARCHAR(100),
    todo_el_dia BOOLEAN DEFAULT FALSE,
    recordatorio_minutos INTEGER DEFAULT 15,
    estado VARCHAR(20) DEFAULT 'confirmado',
    color VARCHAR(7) DEFAULT '#3b82f6',
    creado_por VARCHAR(100),
    creada_en TIMESTAMPTZ DEFAULT NOW(),
    actualizada_en TIMESTAMPTZ DEFAULT NOW()
);

-- 2️⃣ CREAR TABLA DE SINCRONIZACIÓN GOOGLE CALENDAR
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

-- 3️⃣ CREAR ÍNDICES PARA PERFORMANCE
-- ================================================
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_nombre_nora ON agenda_eventos(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_fecha_inicio ON agenda_eventos(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_fecha_fin ON agenda_eventos(fecha_fin);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_tipo ON agenda_eventos(tipo);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_empresa_id ON agenda_eventos(empresa_id);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_tarea_id ON agenda_eventos(tarea_id);

CREATE INDEX IF NOT EXISTS idx_google_calendar_sync_nombre_nora ON google_calendar_sync(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_google_calendar_sync_activo ON google_calendar_sync(sync_activo);

-- 4️⃣ AGREGAR COMENTARIOS A LAS TABLAS
-- ================================================
COMMENT ON TABLE agenda_eventos IS 'Eventos del calendario interno de cada Nora';
COMMENT ON COLUMN agenda_eventos.nombre_nora IS 'Identificador de la instancia Nora';
COMMENT ON COLUMN agenda_eventos.titulo IS 'Título del evento';
COMMENT ON COLUMN agenda_eventos.descripcion IS 'Descripción detallada del evento';
COMMENT ON COLUMN agenda_eventos.fecha_inicio IS 'Fecha y hora de inicio del evento';
COMMENT ON COLUMN agenda_eventos.fecha_fin IS 'Fecha y hora de fin del evento';
COMMENT ON COLUMN agenda_eventos.tipo IS 'Tipo de evento: reunion, cita, llamada, evento, recordatorio';
COMMENT ON COLUMN agenda_eventos.empresa_id IS 'ID de empresa relacionada (FK a cliente_empresas)';
COMMENT ON COLUMN agenda_eventos.tarea_id IS 'ID de tarea relacionada (FK a tareas)';
COMMENT ON COLUMN agenda_eventos.google_event_id IS 'ID del evento en Google Calendar';
COMMENT ON COLUMN agenda_eventos.todo_el_dia IS 'Si el evento dura todo el día';
COMMENT ON COLUMN agenda_eventos.recordatorio_minutos IS 'Minutos antes para recordatorio';
COMMENT ON COLUMN agenda_eventos.estado IS 'Estado del evento: confirmado, tentativo, cancelado';
COMMENT ON COLUMN agenda_eventos.color IS 'Color del evento en formato hex (#RRGGBB)';

COMMENT ON TABLE google_calendar_sync IS 'Configuración de sincronización con Google Calendar';
COMMENT ON COLUMN google_calendar_sync.nombre_nora IS 'Identificador de la instancia Nora';
COMMENT ON COLUMN google_calendar_sync.google_access_token IS 'Token de acceso OAuth2 de Google';
COMMENT ON COLUMN google_calendar_sync.google_refresh_token IS 'Token de renovación OAuth2 de Google';
COMMENT ON COLUMN google_calendar_sync.google_calendar_id IS 'ID del calendario en Google Calendar';
COMMENT ON COLUMN google_calendar_sync.sync_activo IS 'Si la sincronización está activa';

-- 5️⃣ HABILITAR ROW LEVEL SECURITY (RLS)
-- ================================================
ALTER TABLE agenda_eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_calendar_sync ENABLE ROW LEVEL SECURITY;

-- 6️⃣ CREAR POLÍTICAS DE SEGURIDAD
-- ================================================
-- Política para agenda_eventos
DROP POLICY IF EXISTS "agenda_eventos_policy" ON agenda_eventos;
CREATE POLICY "agenda_eventos_policy" ON agenda_eventos
    FOR ALL 
    USING (true)
    WITH CHECK (true);

-- Política para google_calendar_sync
DROP POLICY IF EXISTS "google_calendar_sync_policy" ON google_calendar_sync;
CREATE POLICY "google_calendar_sync_policy" ON google_calendar_sync
    FOR ALL 
    USING (true)
    WITH CHECK (true);

-- 7️⃣ REGISTRAR MÓDULO EN SISTEMA
-- ================================================
-- Insertar módulo si no existe
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta)
SELECT 'agenda', 'Sistema de gestión de eventos y calendario con sincronización Google Calendar', '📅', 'panel_cliente_agenda.panel_cliente_agenda_bp'
WHERE NOT EXISTS (
    SELECT 1 FROM modulos_disponibles WHERE nombre = 'agenda'
);

-- 8️⃣ ACTIVAR MÓDULO PARA AURA
-- ================================================
UPDATE configuracion_bot 
SET modulos = jsonb_set(
    COALESCE(modulos, '{}'), 
    '{agenda}', 
    'true'
)
WHERE nombre_nora = 'aura';

-- 9️⃣ INSERTAR EVENTOS DE EJEMPLO
-- ================================================
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
),
(
    'aura',
    'Workshop equipo',
    'Capacitación en nuevas herramientas de productividad',
    NOW() + INTERVAL '5 days',
    NOW() + INTERVAL '5 days' + INTERVAL '3 hours',
    'evento',
    'Centro de capacitación',
    '#8b5cf6',
    'confirmado'
),
(
    'aura',
    'Recordatorio: Entrega reporte',
    'Completar y enviar reporte mensual de métricas',
    NOW() + INTERVAL '7 days',
    NOW() + INTERVAL '7 days',
    'recordatorio',
    '',
    '#ef4444',
    'confirmado'
);

-- 🔟 CONFIGURACIÓN INICIAL GOOGLE CALENDAR (OPCIONAL)
-- ================================================
INSERT INTO google_calendar_sync (nombre_nora, sync_activo)
SELECT 'aura', FALSE
WHERE NOT EXISTS (
    SELECT 1 FROM google_calendar_sync WHERE nombre_nora = 'aura'
);

-- ================================================
-- ✅ VERIFICACIONES FINALES
-- ================================================

-- Verificar que las tablas se crearon
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('agenda_eventos', 'google_calendar_sync')
ORDER BY table_name;

-- Verificar que el módulo se registró
SELECT nombre, descripcion, icono 
FROM modulos_disponibles 
WHERE nombre = 'agenda';

-- Verificar que el módulo se activó para aura
SELECT nombre_nora, modulos->'agenda' as agenda_activo
FROM configuracion_bot 
WHERE nombre_nora = 'aura';

-- Verificar eventos de ejemplo
SELECT id, nombre_nora, titulo, fecha_inicio, tipo
FROM agenda_eventos 
WHERE nombre_nora = 'aura'
ORDER BY fecha_inicio;

-- Verificar configuración Google Calendar
SELECT nombre_nora, sync_activo, configurado_en
FROM google_calendar_sync 
WHERE nombre_nora = 'aura';

-- ================================================
-- 📋 RESUMEN DE TABLAS CREADAS:
-- 
-- ✅ agenda_eventos (16 columnas)
--    - Eventos principales del calendario
--    - Integración con empresas y tareas
--    - Soporte para Google Calendar sync
--    - RLS habilitado con políticas permisivas
--
-- ✅ google_calendar_sync (12 columnas)  
--    - Configuración OAuth2 Google Calendar
--    - Tokens de acceso y renovación
--    - Estado de sincronización
--    - RLS habilitado con políticas permisivas
--
-- ✅ Índices optimizados para consultas frecuentes
-- ✅ Comentarios de documentación
-- ✅ Módulo registrado en sistema
-- ✅ Módulo activado para 'aura'
-- ✅ 5 eventos de ejemplo insertados
-- ✅ Configuración inicial Google Calendar
-- ================================================
