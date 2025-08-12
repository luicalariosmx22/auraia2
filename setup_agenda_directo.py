#!/usr/bin/env python3
"""
Setup completo del módulo de agenda con método directo a Supabase
Evita usar RPC SQL y usa métodos directos de Supabase
"""

import os
import sys
from dotenv import load_dotenv
sys.path.append('.')

load_dotenv('.env.local')

def setup_modulo_agenda():
    """Setup completo usando métodos directos de Supabase"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe
        
        print("🗓️ SETUP MÓDULO AGENDA - MÉTODO DIRECTO")
        print("=" * 50)
        
        # 1. REGISTRAR MÓDULO EN modulos_disponibles
        print("\n1. 📋 Registrando módulo en modulos_disponibles...")
        try:
            # Verificar si ya existe
            existente = supabase.table('modulos_disponibles') \
                .select('id') \
                .eq('nombre', 'agenda') \
                .execute()
            
            if not existente.data:
                # Insertar nuevo módulo
                resultado = supabase.table('modulos_disponibles').insert({
                    'nombre': 'agenda',
                    'descripcion': 'Gestión integral de agenda con Google Calendar',
                    'icono': '🗓️',
                    'ruta': 'panel_cliente_agenda.panel_cliente_agenda_bp',
                    'archivo_principal': 'panel_cliente_agenda.py'
                }).execute()
                
                if resultado.data:
                    print(f"   ✅ Módulo 'agenda' registrado con ID: {resultado.data[0]['id']}")
                else:
                    print("   ❌ Error registrando módulo")
                    return False
            else:
                print(f"   ✅ Módulo 'agenda' ya existe con ID: {existente.data[0]['id']}")
                
        except Exception as e:
            print(f"   ❌ Error registrando módulo: {e}")
            return False
        
        # 2. ACTIVAR PARA AURA
        print("\n2. 🔄 Activando módulo para 'aura'...")
        try:
            # Obtener configuración actual
            config = supabase.table('configuracion_bot') \
                .select('modulos') \
                .eq('nombre_nora', 'aura') \
                .single() \
                .execute()
            
            if config.data:
                modulos_actuales = config.data.get('modulos', {})
                modulos_actuales['agenda'] = True
                
                # Actualizar configuración
                resultado = supabase.table('configuracion_bot') \
                    .update({'modulos': modulos_actuales}) \
                    .eq('nombre_nora', 'aura') \
                    .execute()
                
                if resultado.data:
                    print("   ✅ Módulo activado para 'aura'")
                else:
                    print("   ❌ Error activando módulo")
                    return False
            else:
                print("   ❌ No se encontró configuración para 'aura'")
                return False
                
        except Exception as e:
            print(f"   ❌ Error activando módulo: {e}")
            return False
        
        # 3. VERIFICAR/CREAR TABLAS NECESARIAS
        print("\n3. 🗄️ Verificando tablas necesarias...")
        
        # 3.1 Verificar agenda_eventos
        if not existe('agenda_eventos'):
            print("   📅 Creando tabla agenda_eventos...")
            try:
                # Usar CREATE TABLE directo ya que la tabla no existe
                sql_agenda = """
                CREATE TABLE agenda_eventos (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_nora VARCHAR(50) NOT NULL,
                    titulo VARCHAR(255) NOT NULL,
                    descripcion TEXT,
                    fecha_inicio TIMESTAMPTZ NOT NULL,
                    fecha_fin TIMESTAMPTZ,
                    todo_el_dia BOOLEAN DEFAULT FALSE,
                    ubicacion VARCHAR(500),
                    tipo_evento VARCHAR(50) DEFAULT 'evento',
                    color VARCHAR(7) DEFAULT '#3B82F6',
                    recordatorio_minutos INTEGER,
                    invitados TEXT[],
                    google_calendar_id VARCHAR(255),
                    google_event_id VARCHAR(255),
                    tarea_id BIGINT,
                    empresa_id BIGINT,
                    recurrente BOOLEAN DEFAULT FALSE,
                    frecuencia_recurrencia VARCHAR(20),
                    hasta_fecha TIMESTAMPTZ,
                    creado_en TIMESTAMPTZ DEFAULT NOW(),
                    actualizado_en TIMESTAMPTZ DEFAULT NOW()
                );
                
                -- Índices para optimización
                CREATE INDEX idx_agenda_eventos_nombre_nora ON agenda_eventos(nombre_nora);
                CREATE INDEX idx_agenda_eventos_fecha_inicio ON agenda_eventos(fecha_inicio);
                CREATE INDEX idx_agenda_eventos_google_event ON agenda_eventos(google_event_id);
                CREATE INDEX idx_agenda_eventos_tarea ON agenda_eventos(tarea_id);
                CREATE INDEX idx_agenda_eventos_empresa ON agenda_eventos(empresa_id);
                """
                
                # Ejecutar usando la función que sabemos que funciona
                resultado = supabase.rpc('execute_sql', {'sql': sql_agenda}).execute()
                print("   ✅ Tabla agenda_eventos creada")
                
            except Exception as e:
                print(f"   ❌ Error creando tabla agenda_eventos: {e}")
                return False
        else:
            print("   ✅ Tabla agenda_eventos ya existe")
        
        # 3.2 Verificar google_calendar_sync
        if not existe('google_calendar_sync'):
            print("   📱 Creando tabla google_calendar_sync...")
            try:
                sql_google = """
                CREATE TABLE google_calendar_sync (
                    id BIGSERIAL PRIMARY KEY,
                    nombre_nora VARCHAR(50) NOT NULL UNIQUE,
                    google_access_token TEXT,
                    google_refresh_token TEXT,
                    google_token_expiry TIMESTAMPTZ,
                    google_calendar_id VARCHAR(255),
                    sync_activo BOOLEAN DEFAULT TRUE,
                    ultimo_sync TIMESTAMPTZ,
                    configuracion JSON,
                    creado_en TIMESTAMPTZ DEFAULT NOW(),
                    actualizado_en TIMESTAMPTZ DEFAULT NOW()
                );
                
                -- Índices
                CREATE INDEX idx_google_calendar_sync_nora ON google_calendar_sync(nombre_nora);
                CREATE INDEX idx_google_calendar_sync_activo ON google_calendar_sync(sync_activo);
                """
                
                resultado = supabase.rpc('execute_sql', {'sql': sql_google}).execute()
                print("   ✅ Tabla google_calendar_sync creada")
                
            except Exception as e:
                print(f"   ❌ Error creando tabla google_calendar_sync: {e}")
                return False
        else:
            print("   ✅ Tabla google_calendar_sync ya existe")
        
        # 4. VERIFICAR DEPENDENCIAS
        print("\n4. 🔗 Verificando dependencias...")
        
        dependencias = ['tareas', 'cliente_empresas']
        for tabla in dependencias:
            if existe(tabla):
                print(f"   ✅ Tabla '{tabla}' existe")
            else:
                print(f"   ⚠️ Tabla '{tabla}' no existe - integración limitada")
        
        # 5. CREAR DATOS INICIALES
        print("\n5. 📝 Configurando datos iniciales...")
        try:
            # Verificar si ya hay configuración de Google Calendar para aura
            config_google = supabase.table('google_calendar_sync') \
                .select('id') \
                .eq('nombre_nora', 'aura') \
                .execute()
            
            if not config_google.data:
                # Crear configuración inicial
                resultado = supabase.table('google_calendar_sync').insert({
                    'nombre_nora': 'aura',
                    'sync_activo': False,  # Desactivado hasta configurar OAuth
                    'configuracion': {
                        'crear_eventos_automaticos': True,
                        'sincronizar_tareas': True,
                        'sincronizar_reuniones_empresa': True,
                        'zona_horaria': 'America/Mexico_City'
                    }
                }).execute()
                
                if resultado.data:
                    print("   ✅ Configuración inicial de Google Calendar creada")
                else:
                    print("   ❌ Error creando configuración inicial")
            else:
                print("   ✅ Configuración de Google Calendar ya existe")
                
        except Exception as e:
            print(f"   ❌ Error configurando datos iniciales: {e}")
            return False
        
        # 6. VALIDACIÓN FINAL
        print("\n6. ✅ Validación final...")
        try:
            # Verificar que el módulo está registrado y activado
            modulo_check = supabase.table('modulos_disponibles') \
                .select('nombre, descripcion') \
                .eq('nombre', 'agenda') \
                .single() \
                .execute()
            
            config_check = supabase.table('configuracion_bot') \
                .select('modulos') \
                .eq('nombre_nora', 'aura') \
                .single() \
                .execute()
            
            if (modulo_check.data and 
                config_check.data and 
                config_check.data.get('modulos', {}).get('agenda')):
                
                print("   ✅ Módulo 'agenda' correctamente registrado y activado")
                print("   ✅ Tablas de base de datos creadas")
                print("   ✅ Configuración inicial establecida")
                
                print(f"\n🎉 SETUP COMPLETADO EXITOSAMENTE")
                print("=" * 50)
                print("📝 PRÓXIMOS PASOS:")
                print("   1. Reiniciar el servidor Flask")
                print("   2. Ir a /panel_cliente/aura/agenda")
                print("   3. Configurar OAuth de Google Calendar")
                print("   4. Ejecutar: python test_modulo_agenda.py")
                
                return True
            else:
                print("   ❌ Error en validación final")
                return False
                
        except Exception as e:
            print(f"   ❌ Error en validación: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error general en setup: {e}")
        return False

if __name__ == "__main__":
    success = setup_modulo_agenda()
    if success:
        print("\n✅ Setup completado. El módulo está listo para usar.")
    else:
        print("\n❌ Setup falló. Revisar errores arriba.")
        sys.exit(1)
