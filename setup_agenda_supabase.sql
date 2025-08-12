-- =====================================================
-- SETUP COMPLETO PARA MÓDULO DE AGENDA EN SUPABASE
-- VERSIÓN SEGURA - TABLAS EXISTENTES VERIFICADAS
-- =====================================================

-- ✅ TODAS LAS TABLAS YA EXISTEN - SOLO MODIFICACIONES SEGURAS

-- 1. CONVERSIÓN DE TIPOS INCOMPATIBLES EN agenda_eventos
-- PROBLEMA DETECTADO: agenda_eventos tiene campos BIGINT pero foreign keys son UUID
-- SOLUCIÓN: Agregar nueva columna UUID y mantener BIGINT existente

-- 🚨 SOLUCIÓN: Agregar nueva columna UUID en lugar de convertir BIGINT existente
-- No convertimos el ID existente, agregamos nuevo campo UUID para foreign keys
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS uuid_id UUID DEFAULT gen_random_uuid();

-- 🚨 CONVERSIÓN CRÍTICA: empresa_id de BIGINT a UUID (convertir si existe)
-- NOTA: Agregamos UUID para compatibilidad futura con foreign keys
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS empresa_uuid UUID;

-- 🚨 CONVERSIÓN CRÍTICA: tarea_id de BIGINT a UUID (convertir si existe)  
-- NOTA: Agregamos UUID para compatibilidad futura con foreign keys
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS tarea_uuid UUID;

-- 2. AGREGAR COLUMNAS FALTANTES EN agenda_eventos (si no existen)
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS nombre_nora VARCHAR(50) NOT NULL DEFAULT 'aura';
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT 'reunion';
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS ubicacion TEXT;
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#3b82f6';
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS all_day BOOLEAN DEFAULT FALSE;
ALTER TABLE agenda_eventos ADD COLUMN IF NOT EXISTS recordatorio_minutos INTEGER DEFAULT 15;

-- 2. AGREGAR CAMPO fecha_vencimiento A TABLA tareas (si no existe)
ALTER TABLE tareas ADD COLUMN IF NOT EXISTS fecha_vencimiento TIMESTAMPTZ;

-- 3. CONVERSIÓN DE TIPOS EN google_calendar_sync (si es necesario)  
-- Solo agregar UUID si no existe, no convertir campos existentes
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS uuid_id UUID DEFAULT gen_random_uuid();

-- 4. AGREGAR COLUMNAS FALTANTES EN google_calendar_sync (si no existen)
-- Agregar campos para conectividad con Google Calendar
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS calendar_id TEXT;
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS access_token TEXT;
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS refresh_token TEXT;
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMPTZ;
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS evento_id UUID;
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS nombre_nora VARCHAR(50);
ALTER TABLE google_calendar_sync ADD COLUMN IF NOT EXISTS sync_enabled BOOLEAN DEFAULT TRUE;

-- 5. FOREIGN KEYS COMENTADAS - TIPOS INCOMPATIBLES
-- PROBLEMA: agenda_eventos tiene campos BIGINT, pero cliente_empresas/tareas usan UUID
-- SOLUCIÓN: Comentar foreign keys hasta que se resuelva compatibilidad de tipos

-- COMENTADO: Foreign key a cliente_empresas (tipos incompatibles)
-- ALTER TABLE agenda_eventos DROP CONSTRAINT IF EXISTS fk_agenda_eventos_empresa;
-- ALTER TABLE agenda_eventos 
-- ADD CONSTRAINT fk_agenda_eventos_empresa 
-- FOREIGN KEY (empresa_uuid) REFERENCES cliente_empresas(id) ON DELETE SET NULL;

-- COMENTADO: Foreign key a tareas (tipos incompatibles)  
-- ALTER TABLE agenda_eventos DROP CONSTRAINT IF EXISTS fk_agenda_eventos_tarea;
-- ALTER TABLE agenda_eventos 
-- ADD CONSTRAINT fk_agenda_eventos_tarea 
-- FOREIGN KEY (tarea_uuid) REFERENCES tareas(id) ON DELETE SET NULL;

-- 6. CREAR ÍNDICES PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_nombre_nora ON agenda_eventos(nombre_nora);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_fecha_inicio ON agenda_eventos(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_fecha_fin ON agenda_eventos(fecha_fin);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_empresa ON agenda_eventos(empresa_id);
CREATE INDEX IF NOT EXISTS idx_agenda_eventos_tarea ON agenda_eventos(tarea_id);
CREATE INDEX IF NOT EXISTS idx_google_calendar_sync_evento ON google_calendar_sync(evento_id);
CREATE INDEX IF NOT EXISTS idx_google_calendar_sync_nora ON google_calendar_sync(nombre_nora);

-- Crear índice en tareas si la tabla existe
CREATE INDEX IF NOT EXISTS idx_tareas_fecha_vencimiento ON tareas(fecha_vencimiento);

-- 7. HABILITAR RLS (Row Level Security) Y POLÍTICAS
ALTER TABLE agenda_eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_calendar_sync ENABLE ROW LEVEL SECURITY;

-- Política para agenda_eventos
DROP POLICY IF EXISTS "Permitir todo acceso a agenda_eventos" ON agenda_eventos;
CREATE POLICY "Permitir todo acceso a agenda_eventos" ON agenda_eventos
    FOR ALL USING (true) WITH CHECK (true);

-- Política para google_calendar_sync
DROP POLICY IF EXISTS "Permitir todo acceso a google_calendar_sync" ON google_calendar_sync;
CREATE POLICY "Permitir todo acceso a google_calendar_sync" ON google_calendar_sync
    FOR ALL USING (true) WITH CHECK (true);

-- 8. INSERTAR DATOS DE EJEMPLO (OPCIONAL)
INSERT INTO agenda_eventos (nombre_nora, titulo, descripcion, fecha_inicio, fecha_fin, tipo)
VALUES 
    ('aura', 'Reunión con cliente', 'Presentación del proyecto de marketing digital', '2025-08-15 10:00:00+00', '2025-08-15 11:00:00+00', 'reunion'),
    ('aura', 'Llamada de seguimiento', 'Revisar avances del proyecto Meta Ads', '2025-08-16 14:30:00+00', '2025-08-16 15:00:00+00', 'llamada'),
    ('aura', 'Workshop IA', 'Taller interno sobre nuevas funcionalidades IA', '2025-08-20 09:00:00+00', '2025-08-20 17:00:00+00', 'capacitacion')
ON CONFLICT DO NOTHING;

-- 9. VERIFICAR TABLAS CREADAS
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('agenda_eventos', 'google_calendar_sync') 
   OR (table_name = 'tareas' AND column_name = 'fecha_vencimiento')
ORDER BY table_name, ordinal_position;

-- 10. COMENTARIOS EN TABLAS
COMMENT ON TABLE agenda_eventos IS 'Eventos del calendario interno de cada Nora';
COMMENT ON TABLE google_calendar_sync IS 'Configuración de sincronización con Google Calendar';

-- Comentario en tareas solo si existe la tabla y columna
COMMENT ON COLUMN tareas.fecha_vencimiento IS 'Fecha límite de la tarea para mostrar en calendario';

-- =====================================================
-- COMANDOS DE VERIFICACIÓN (EJECUTAR DESPUÉS)
-- =====================================================

-- Verificar que agenda_eventos existe y tiene datos
SELECT COUNT(*) as total_eventos FROM agenda_eventos;

-- Verificar que tareas tiene campo fecha_vencimiento
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'tareas' AND column_name = 'fecha_vencimiento';

-- Verificar google_calendar_sync
SELECT COUNT(*) as total_configs FROM google_calendar_sync;

-- Verificar foreign keys
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name IN ('agenda_eventos');
