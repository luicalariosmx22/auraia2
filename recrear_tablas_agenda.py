#!/usr/bin/env python3
"""
Script para recrear tablas agenda con estructura correcta y permisos
"""

import os
import sys
from datetime import datetime

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase

def main():
    print("🔧 RECREANDO TABLAS AGENDA CON ESTRUCTURA CORRECTA")
    print("=" * 65)
    
    # 1. Verificar estructura actual de las tablas
    print("\n1. 📋 Verificando estructura actual:")
    verificar_estructura_actual()
    
    # 2. Recrear tablas con estructura correcta
    print("\n2. 🔨 Recreando tablas:")
    recrear_tablas_agenda()
    
    # 3. Configurar permisos RLS
    print("\n3. 🔐 Configurando permisos:")
    configurar_permisos_rls()
    
    # 4. Insertar datos iniciales
    print("\n4. 📤 Insertando datos iniciales:")
    insertar_datos_iniciales()
    
    # 5. Verificación final
    print("\n5. ✅ Verificación final:")
    verificacion_final()

def verificar_estructura_actual():
    """Verifica qué existe actualmente"""
    
    # Verificar usando información del schema
    try:
        # Consulta para ver la estructura de la tabla
        sql_info = """
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name IN ('agenda_eventos', 'google_calendar_sync')
        ORDER BY table_name, ordinal_position;
        """
        
        result = supabase.rpc('execute_sql', {'sql': sql_info}).execute()
        print(f"   📊 Estructura actual de tablas:")
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"   ⚠️ No se pudo verificar estructura: {str(e)[:150]}")

def recrear_tablas_agenda():
    """Recrear tablas con estructura correcta"""
    
    # SQL para recrear agenda_eventos
    sql_agenda_eventos = """
    -- Eliminar tabla si existe
    DROP TABLE IF EXISTS agenda_eventos CASCADE;
    
    -- Crear tabla agenda_eventos
    CREATE TABLE agenda_eventos (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nombre_nora VARCHAR(50) NOT NULL,
        titulo VARCHAR(200) NOT NULL,
        descripcion TEXT,
        fecha_inicio TIMESTAMPTZ NOT NULL,
        fecha_fin TIMESTAMPTZ NOT NULL,
        todo_el_dia BOOLEAN DEFAULT FALSE,
        cliente_id UUID,
        empresa_id UUID,
        ubicacion VARCHAR(500),
        tipo_evento VARCHAR(50) DEFAULT 'cita',
        estado VARCHAR(20) DEFAULT 'confirmado',
        recordatorio_minutos INTEGER DEFAULT 15,
        google_event_id VARCHAR(1024),
        tarea_id UUID,
        creado_en TIMESTAMPTZ DEFAULT NOW(),
        actualizado_en TIMESTAMPTZ DEFAULT NOW(),
        
        -- Foreign keys
        CONSTRAINT fk_agenda_cliente FOREIGN KEY (cliente_id) REFERENCES usuarios_clientes(id),
        CONSTRAINT fk_agenda_empresa FOREIGN KEY (empresa_id) REFERENCES cliente_empresas(id),
        CONSTRAINT fk_agenda_tarea FOREIGN KEY (tarea_id) REFERENCES tareas(id)
    );
    
    -- Índices para agenda_eventos
    CREATE INDEX idx_agenda_eventos_nombre_nora ON agenda_eventos(nombre_nora);
    CREATE INDEX idx_agenda_eventos_fecha_inicio ON agenda_eventos(fecha_inicio);
    CREATE INDEX idx_agenda_eventos_cliente ON agenda_eventos(cliente_id);
    CREATE INDEX idx_agenda_eventos_empresa ON agenda_eventos(empresa_id);
    CREATE INDEX idx_agenda_eventos_google_id ON agenda_eventos(google_event_id);
    """
    
    # SQL para recrear google_calendar_sync
    sql_google_sync = """
    -- Eliminar tabla si existe
    DROP TABLE IF EXISTS google_calendar_sync CASCADE;
    
    -- Crear tabla google_calendar_sync
    CREATE TABLE google_calendar_sync (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nombre_nora VARCHAR(50) UNIQUE NOT NULL,
        access_token TEXT,
        refresh_token TEXT,
        token_expiry TIMESTAMPTZ,
        calendar_id VARCHAR(255) DEFAULT 'primary',
        sync_enabled BOOLEAN DEFAULT FALSE,
        last_sync TIMESTAMPTZ,
        scopes TEXT DEFAULT 'https://www.googleapis.com/auth/calendar',
        creado_en TIMESTAMPTZ DEFAULT NOW(),
        actualizado_en TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Índices para google_calendar_sync
    CREATE INDEX idx_google_sync_nombre_nora ON google_calendar_sync(nombre_nora);
    CREATE INDEX idx_google_sync_enabled ON google_calendar_sync(sync_enabled);
    """
    
    try:
        print("   🔨 Recreando tabla agenda_eventos...")
        result1 = supabase.rpc('execute_sql', {'sql': sql_agenda_eventos}).execute()
        print(f"   ✅ agenda_eventos recreada")
        
        print("   🔨 Recreando tabla google_calendar_sync...")
        result2 = supabase.rpc('execute_sql', {'sql': sql_google_sync}).execute()
        print(f"   ✅ google_calendar_sync recreada")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error recreando tablas: {str(e)[:200]}")
        return False

def configurar_permisos_rls():
    """Configurar Row Level Security y permisos"""
    
    # Configurar RLS para agenda_eventos
    sql_rls_agenda = """
    -- Habilitar RLS en agenda_eventos
    ALTER TABLE agenda_eventos ENABLE ROW LEVEL SECURITY;
    
    -- Política para lectura/escritura por nombre_nora
    CREATE POLICY "agenda_eventos_policy" ON agenda_eventos
    FOR ALL USING (true);
    
    -- Grants para anon y authenticated
    GRANT ALL ON agenda_eventos TO anon;
    GRANT ALL ON agenda_eventos TO authenticated;
    GRANT ALL ON agenda_eventos TO service_role;
    """
    
    # Configurar RLS para google_calendar_sync
    sql_rls_google = """
    -- Habilitar RLS en google_calendar_sync
    ALTER TABLE google_calendar_sync ENABLE ROW LEVEL SECURITY;
    
    -- Política para lectura/escritura
    CREATE POLICY "google_sync_policy" ON google_calendar_sync
    FOR ALL USING (true);
    
    -- Grants
    GRANT ALL ON google_calendar_sync TO anon;
    GRANT ALL ON google_calendar_sync TO authenticated;
    GRANT ALL ON google_calendar_sync TO service_role;
    """
    
    try:
        print("   🔐 Configurando permisos agenda_eventos...")
        result1 = supabase.rpc('execute_sql', {'sql': sql_rls_agenda}).execute()
        print(f"   ✅ Permisos agenda_eventos configurados")
        
        print("   🔐 Configurando permisos google_calendar_sync...")
        result2 = supabase.rpc('execute_sql', {'sql': sql_rls_google}).execute()
        print(f"   ✅ Permisos google_calendar_sync configurados")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ Advertencia permisos: {str(e)[:200]}")
        return False

def insertar_datos_iniciales():
    """Insertar datos iniciales en google_calendar_sync"""
    
    # Datos iniciales para aura
    sql_insert = """
    INSERT INTO google_calendar_sync (
        nombre_nora, access_token, refresh_token, calendar_id, 
        sync_enabled, scopes, creado_en, actualizado_en
    ) VALUES (
        'aura', NULL, NULL, 'primary', FALSE,
        'https://www.googleapis.com/auth/calendar',
        NOW(), NOW()
    ) ON CONFLICT (nombre_nora) DO UPDATE SET
        actualizado_en = NOW();
    """
    
    try:
        print("   📤 Insertando configuración inicial para 'aura'...")
        result = supabase.rpc('execute_sql', {'sql': sql_insert}).execute()
        print(f"   ✅ Datos iniciales insertados")
        return True
        
    except Exception as e:
        print(f"   ❌ Error insertando datos: {str(e)[:200]}")
        return False

def verificacion_final():
    """Verificación final del setup"""
    
    # Test de acceso a agenda_eventos
    try:
        result = supabase.table('agenda_eventos').select('*').limit(1).execute()
        print(f"   ✅ agenda_eventos: Accesible")
    except Exception as e:
        print(f"   ❌ agenda_eventos: {str(e)[:100]}")
    
    # Test de acceso a google_calendar_sync
    try:
        result = supabase.table('google_calendar_sync').select('*').limit(1).execute()
        print(f"   ✅ google_calendar_sync: Accesible")
    except Exception as e:
        print(f"   ❌ google_calendar_sync: {str(e)[:100]}")
    
    # Test de inserción de evento de prueba
    try:
        evento_prueba = {
            'nombre_nora': 'aura',
            'titulo': 'Test Setup',
            'descripcion': 'Evento de prueba para verificar funcionamiento',
            'fecha_inicio': datetime.now().isoformat(),
            'fecha_fin': (datetime.now()).isoformat(),
            'tipo_evento': 'test'
        }
        
        result = supabase.table('agenda_eventos').insert(evento_prueba).execute()
        if result.data:
            # Eliminar evento de prueba
            supabase.table('agenda_eventos').delete().eq('titulo', 'Test Setup').execute()
            print(f"   ✅ Test de inserción: EXITOSO")
        
    except Exception as e:
        print(f"   ❌ Test de inserción: {str(e)[:100]}")
    
    # Mostrar configuración final
    print(f"\n📋 URLs del módulo agenda (listas para usar):")
    print(f"   • Dashboard: http://localhost:5000/panel_cliente/aura/agenda")
    print(f"   • API eventos: http://localhost:5000/panel_cliente/aura/agenda/api/eventos")
    print(f"   • Google OAuth: http://localhost:5000/panel_cliente/aura/agenda/google/auth")

if __name__ == "__main__":
    try:
        main()
        print(f"\n🎉 SETUP AGENDA COMPLETADO EXITOSAMENTE")
        print(f"=" * 65)
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        print(f"💡 Revisar configuración de Supabase")
