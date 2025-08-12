"""
Script para configurar el módulo de agenda completo
Crea tablas, registra el módulo y configura integraciones

Ejecutar: python setup_modulo_agenda.py
"""

import os
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

load_dotenv()

def crear_tabla_agenda_eventos():
    """Crea la tabla principal de eventos de agenda"""
    try:
        print("📅 Creando tabla agenda_eventos...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS agenda_eventos (
            id BIGSERIAL PRIMARY KEY,
            nombre_nora VARCHAR(50) NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            descripcion TEXT,
            fecha_inicio TIMESTAMPTZ NOT NULL,
            fecha_fin TIMESTAMPTZ,
            ubicacion VARCHAR(300),
            tipo VARCHAR(50) DEFAULT 'reunion',
            empresa_id BIGINT REFERENCES cliente_empresas(id),
            tarea_id BIGINT REFERENCES tareas(id),
            google_event_id VARCHAR(100),
            todo_el_dia BOOLEAN DEFAULT FALSE,
            recordatorio_minutos INTEGER DEFAULT 15,
            estado VARCHAR(20) DEFAULT 'confirmado',
            color VARCHAR(7) DEFAULT '#3b82f6',
            creado_por VARCHAR(100),
            creada_en TIMESTAMPTZ DEFAULT NOW(),
            actualizada_en TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_agenda_eventos_nora ON agenda_eventos(nombre_nora);
        CREATE INDEX IF NOT EXISTS idx_agenda_eventos_fecha ON agenda_eventos(fecha_inicio);
        CREATE INDEX IF NOT EXISTS idx_agenda_eventos_empresa ON agenda_eventos(empresa_id);
        CREATE INDEX IF NOT EXISTS idx_agenda_eventos_tarea ON agenda_eventos(tarea_id);
        CREATE INDEX IF NOT EXISTS idx_agenda_eventos_google ON agenda_eventos(google_event_id);
        """
        
        supabase.rpc('execute_sql', {'sql': sql}).execute()
        print("✅ Tabla agenda_eventos creada")
        
    except Exception as e:
        print(f"❌ Error creando tabla agenda_eventos: {e}")

def crear_tabla_google_calendar_sync():
    """Crea la tabla para sincronización con Google Calendar"""
    try:
        print("🔄 Creando tabla google_calendar_sync...")
        
        sql = """
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

        CREATE INDEX IF NOT EXISTS idx_google_sync_nora ON google_calendar_sync(nombre_nora);
        CREATE INDEX IF NOT EXISTS idx_google_sync_activo ON google_calendar_sync(sync_activo);
        """
        
        supabase.rpc('execute_sql', {'sql': sql}).execute()
        print("✅ Tabla google_calendar_sync creada")
        
    except Exception as e:
        print(f"❌ Error creando tabla google_calendar_sync: {e}")

def registrar_modulo_agenda():
    """Registra el módulo de agenda en modulos_disponibles"""
    try:
        print("📋 Registrando módulo agenda...")
        
        # Verificar si ya existe
        resultado = supabase.table('modulos_disponibles') \
            .select('id') \
            .eq('nombre', 'agenda') \
            .execute()
        
        if resultado.data:
            print("⚠️ Módulo agenda ya está registrado")
            return
        
        # Registrar módulo
        supabase.table('modulos_disponibles').insert({
            'nombre': 'agenda',
            'descripcion': 'Gestión de eventos, citas y sincronización con Google Calendar',
            'icono': '📅',
            'ruta': 'panel_cliente_agenda.panel_cliente_agenda_bp',
            'archivo_principal': 'panel_cliente_agenda.py',
            'activo': True
        }).execute()
        
        print("✅ Módulo agenda registrado en modulos_disponibles")
        
    except Exception as e:
        print(f"❌ Error registrando módulo: {e}")

def activar_modulo_para_nora(nombre_nora='aura'):
    """Activa el módulo de agenda para una Nora específica"""
    try:
        print(f"🔓 Activando módulo agenda para {nombre_nora}...")
        
        # Obtener configuración actual
        resultado = supabase.table('configuracion_bot') \
            .select('modulos') \
            .eq('nombre_nora', nombre_nora) \
            .single() \
            .execute()
        
        if not resultado.data:
            print(f"❌ No se encontró configuración para {nombre_nora}")
            return
        
        modulos = resultado.data.get('modulos', {})
        modulos['agenda'] = True
        
        # Actualizar configuración
        supabase.table('configuracion_bot') \
            .update({'modulos': modulos}) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        print(f"✅ Módulo agenda activado para {nombre_nora}")
        
    except Exception as e:
        print(f"❌ Error activando módulo: {e}")

def crear_eventos_ejemplo(nombre_nora='aura'):
    """Crea algunos eventos de ejemplo para testing"""
    try:
        print("📝 Creando eventos de ejemplo...")
        
        from datetime import datetime, timedelta
        
        eventos_ejemplo = [
            {
                'nombre_nora': nombre_nora,
                'titulo': 'Reunión de seguimiento - Cliente ABC',
                'descripcion': 'Revisión del progreso del proyecto y próximos pasos',
                'fecha_inicio': (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0).isoformat(),
                'fecha_fin': (datetime.now() + timedelta(days=1)).replace(hour=11, minute=0).isoformat(),
                'ubicacion': 'Oficina principal',
                'tipo': 'reunion',
                'color': '#3b82f6'
            },
            {
                'nombre_nora': nombre_nora,
                'titulo': 'Llamada con proveedor',
                'descripcion': 'Negociación de nuevos precios y condiciones',
                'fecha_inicio': (datetime.now() + timedelta(days=2)).replace(hour=14, minute=30).isoformat(),
                'fecha_fin': (datetime.now() + timedelta(days=2)).replace(hour=15, minute=30).isoformat(),
                'tipo': 'llamada',
                'color': '#10b981'
            },
            {
                'nombre_nora': nombre_nora,
                'titulo': 'Presentación nueva campaña',
                'descripcion': 'Presentar estrategia digital para Q2',
                'fecha_inicio': (datetime.now() + timedelta(days=3)).replace(hour=16, minute=0).isoformat(),
                'fecha_fin': (datetime.now() + timedelta(days=3)).replace(hour=17, minute=0).isoformat(),
                'ubicacion': 'Sala de juntas',
                'tipo': 'evento',
                'color': '#8b5cf6'
            }
        ]
        
        for evento in eventos_ejemplo:
            supabase.table('agenda_eventos').insert(evento).execute()
        
        print(f"✅ Creados {len(eventos_ejemplo)} eventos de ejemplo")
        
    except Exception as e:
        print(f"❌ Error creando eventos de ejemplo: {e}")

def verificar_configuracion():
    """Verifica que todo esté configurado correctamente"""
    try:
        print("🔍 Verificando configuración...")
        
        # Verificar tablas
        tablas = ['agenda_eventos', 'google_calendar_sync', 'modulos_disponibles', 'configuracion_bot']
        for tabla in tablas:
            try:
                resultado = supabase.table(tabla).select('*').limit(1).execute()
                print(f"✅ Tabla {tabla}: OK")
            except Exception as e:
                print(f"❌ Tabla {tabla}: Error - {e}")
        
        # Verificar módulo registrado
        modulo = supabase.table('modulos_disponibles') \
            .select('*') \
            .eq('nombre', 'agenda') \
            .execute()
        
        if modulo.data:
            print("✅ Módulo agenda registrado")
        else:
            print("❌ Módulo agenda NO registrado")
        
        # Verificar activación para aura
        config = supabase.table('configuracion_bot') \
            .select('modulos') \
            .eq('nombre_nora', 'aura') \
            .single() \
            .execute()
        
        if config.data and config.data.get('modulos', {}).get('agenda'):
            print("✅ Módulo activado para aura")
        else:
            print("❌ Módulo NO activado para aura")
        
        # Verificar eventos
        eventos = supabase.table('agenda_eventos') \
            .select('id') \
            .eq('nombre_nora', 'aura') \
            .execute()
        
        print(f"📅 Eventos en BD: {len(eventos.data or [])}")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

def main():
    """Función principal que ejecuta todo el setup"""
    print("🚀 CONFIGURANDO MÓDULO DE AGENDA")
    print("=" * 50)
    
    # 1. Crear tablas
    crear_tabla_agenda_eventos()
    crear_tabla_google_calendar_sync()
    
    # 2. Registrar módulo
    registrar_modulo_agenda()
    
    # 3. Activar para aura
    activar_modulo_para_nora('aura')
    
    # 4. Crear eventos de ejemplo
    crear_eventos_ejemplo('aura')
    
    # 5. Verificar todo
    print("\n" + "=" * 50)
    verificar_configuracion()
    
    print("\n" + "=" * 50)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("\n📋 Próximos pasos:")
    print("1. Configuar variables Google Calendar (opcional):")
    print("   - GOOGLE_CLIENT_ID")
    print("   - GOOGLE_CLIENT_SECRET") 
    print("   - BASE_URL")
    print("\n2. Agregar en registro_dinamico.py:")
    print('   if "agenda" in modulos:')
    print('       from clientes.aura.routes.panel_cliente_agenda import panel_cliente_agenda_bp')
    print('       safe_register_blueprint(app, panel_cliente_agenda_bp)')
    print(f'\n3. Acceder: http://localhost:5000/panel_cliente/aura/agenda/')
    print("\n🎯 ¡El módulo de agenda está listo para usar!")

if __name__ == "__main__":
    main()
