#!/usr/bin/env python3
"""
Script para arreglar permisos y completar setup del módulo agenda
Detecta y corrige problemas de permisos en las tablas nuevas
"""

import os
import sys
from datetime import datetime

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.utils.supabase_client import supabase

def main():
    print("🔧 REPARANDO PERMISOS Y COMPLETANDO SETUP AGENDA")
    print("=" * 60)
    
    # 1. Verificar estado actual
    print("\n1. 📋 Verificando estado actual:")
    verificar_estado_tablas()
    
    # 2. Intentar insertar datos con diferentes métodos
    print("\n2. 🔄 Probando inserción de datos:")
    insertar_datos_google_calendar()
    
    # 3. Verificar que el módulo funciona
    print("\n3. ✅ Verificación final:")
    verificar_modulo_completo()

def verificar_estado_tablas():
    """Verifica estado de las tablas agenda"""
    tablas = ['agenda_eventos', 'google_calendar_sync', 'modulos_disponibles', 'configuracion_bot']
    
    for tabla in tablas:
        try:
            # Test básico de acceso
            result = supabase.table(tabla).select('*').limit(1).execute()
            
            if result.data is not None:
                count = len(result.data)
                print(f"   ✅ {tabla}: Accesible ({count} registros)")
            else:
                print(f"   ⚠️ {tabla}: Accesible pero sin datos")
                
        except Exception as e:
            error_msg = str(e)
            if 'permission denied' in error_msg:
                print(f"   ❌ {tabla}: Sin permisos de acceso")
            elif '404' in error_msg or 'not found' in error_msg:
                print(f"   ❌ {tabla}: No existe")
            else:
                print(f"   ⚠️ {tabla}: Error - {error_msg[:100]}")

def insertar_datos_google_calendar():
    """Intenta insertar datos iniciales en google_calendar_sync"""
    
    # Datos iniciales para la tabla
    datos_iniciales = {
        'nombre_nora': 'aura',
        'google_access_token': None,
        'google_refresh_token': None,
        'calendar_id': 'primary',
        'activo': False,
        'configurado': False,
        'scopes': 'https://www.googleapis.com/auth/calendar',
        'creado_en': datetime.now().isoformat(),
        'actualizado_en': datetime.now().isoformat()
    }
    
    print(f"   📤 Insertando configuración inicial para 'aura'...")
    
    # Método 1: INSERT directo
    try:
        result = supabase.table('google_calendar_sync').insert(datos_iniciales).execute()
        if result.data:
            print(f"   ✅ Método INSERT directo: ÉXITO")
            return True
    except Exception as e:
        print(f"   ❌ Método INSERT directo: {str(e)[:150]}")
    
    # Método 2: UPSERT
    try:
        result = supabase.table('google_calendar_sync').upsert(datos_iniciales).execute()
        if result.data:
            print(f"   ✅ Método UPSERT: ÉXITO")
            return True
    except Exception as e:
        print(f"   ❌ Método UPSERT: {str(e)[:150]}")
    
    # Método 3: Via RPC execute_sql
    try:
        sql_insert = f"""
        INSERT INTO google_calendar_sync (
            nombre_nora, google_access_token, google_refresh_token, 
            calendar_id, activo, configurado, scopes, creado_en, actualizado_en
        ) VALUES (
            'aura', NULL, NULL, 'primary', false, false,
            'https://www.googleapis.com/auth/calendar',
            NOW(), NOW()
        ) ON CONFLICT (nombre_nora) DO NOTHING;
        """
        
        result = supabase.rpc('execute_sql', {'sql': sql_insert}).execute()
        print(f"   ✅ Método RPC execute_sql: ÉXITO")
        return True
    except Exception as e:
        print(f"   ❌ Método RPC execute_sql: {str(e)[:150]}")
    
    # Método 4: Verificar si ya existe el registro
    try:
        existing = supabase.table('google_calendar_sync') \
            .select('*') \
            .eq('nombre_nora', 'aura') \
            .execute()
        
        if existing.data:
            print(f"   ℹ️ El registro ya existe: {len(existing.data)} registros para 'aura'")
            return True
    except Exception as e:
        print(f"   ❌ Método verificar existente: {str(e)[:150]}")
    
    print(f"   ⚠️ No se pudo insertar datos iniciales")
    return False

def verificar_modulo_completo():
    """Verificación final del módulo agenda"""
    
    # 1. Verificar registro en modulos_disponibles
    try:
        modulo = supabase.table('modulos_disponibles') \
            .select('*') \
            .eq('nombre', 'agenda') \
            .single() \
            .execute()
        
        if modulo.data:
            print(f"   ✅ Módulo registrado: {modulo.data['descripcion']}")
        else:
            print(f"   ❌ Módulo NO registrado")
    except Exception as e:
        print(f"   ⚠️ Error verificando módulo: {str(e)[:100]}")
    
    # 2. Verificar activación para aura
    try:
        config = supabase.table('configuracion_bot') \
            .select('modulos') \
            .eq('nombre_nora', 'aura') \
            .single() \
            .execute()
        
        if config.data and config.data.get('modulos', {}).get('agenda'):
            print(f"   ✅ Módulo activo para 'aura'")
        else:
            print(f"   ❌ Módulo NO activo para 'aura'")
    except Exception as e:
        print(f"   ⚠️ Error verificando activación: {str(e)[:100]}")
    
    # 3. Verificar archivos del módulo
    archivos_requeridos = [
        'clientes/aura/routes/panel_cliente_agenda/panel_cliente_agenda.py',
        'clientes/aura/routes/panel_cliente_agenda/google_calendar_service.py',
        'clientes/aura/templates/panel_cliente_agenda/index.html'
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ Archivo existe: {archivo}")
        else:
            print(f"   ❌ Archivo faltante: {archivo}")
    
    # 4. Verificar dependencias de Python
    try:
        import google.auth
        import google.oauth2.credentials
        import googleapiclient.discovery
        print(f"   ✅ Dependencias Google Calendar: Instaladas")
    except ImportError as e:
        print(f"   ❌ Dependencias faltantes: {str(e)}")
    
    # 5. Mostrar URLs del módulo
    print(f"\n📋 URLs del módulo agenda:")
    print(f"   • Dashboard: /panel_cliente/aura/agenda")
    print(f"   • API eventos: /panel_cliente/aura/agenda/api/eventos")
    print(f"   • Google Auth: /panel_cliente/aura/agenda/google/auth")
    print(f"   • Google Callback: /panel_cliente/aura/agenda/google/callback")

if __name__ == "__main__":
    try:
        main()
        print(f"\n🎉 PROCESO COMPLETADO")
        print(f"=" * 60)
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        print(f"💡 Revisar permisos de base de datos y configuración")
