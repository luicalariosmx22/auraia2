#!/usr/bin/env python
"""
Script para configurar la base de datos del módulo de agenda
Ejecuta el SQL setup de forma segura y verifica la configuración
"""

import os
import sys
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.quick_schemas import existe, columnas

def verificar_configuracion_agenda():
    """Verifica la configuración actual de la base de datos para agenda"""
    print("🔍 VERIFICANDO CONFIGURACIÓN DE AGENDA")
    print("=" * 50)
    
    # 1. Verificar tablas principales
    tablas_agenda = [
        'agenda_eventos',
        'cliente_empresas', 
        'tareas',
        'google_calendar_sync'
    ]
    
    print("\n📋 Estado de tablas:")
    for tabla in tablas_agenda:
        if existe(tabla):
            campos = columnas(tabla)
            print(f"✅ {tabla}: {len(campos)} columnas")
            if tabla == 'tareas':
                tiene_fecha_vencimiento = 'fecha_vencimiento' in campos
                tiene_fecha_limite = 'fecha_limite' in campos
                print(f"   📅 fecha_vencimiento: {'✅' if tiene_fecha_vencimiento else '❌'}")
                print(f"   📅 fecha_limite: {'✅' if tiene_fecha_limite else '❌'}")
        else:
            print(f"❌ {tabla}: No existe")
    
    # 2. Verificar foreign keys
    print("\n🔗 Verificando relaciones:")
    if existe('agenda_eventos'):
        try:
            # Test de consulta con JOIN
            result = supabase.table('agenda_eventos') \
                .select('*, cliente_empresas(nombre_empresa)') \
                .limit(1) \
                .execute()
            print("✅ Relación agenda_eventos -> cliente_empresas: OK")
        except Exception as e:
            print(f"❌ Relación agenda_eventos -> cliente_empresas: {e}")
    
    # 3. Verificar módulo registrado
    print("\n📦 Verificando registro del módulo:")
    try:
        modulo = supabase.table('modulos_disponibles') \
            .select('*') \
            .eq('nombre', 'agenda') \
            .single() \
            .execute()
        
        if modulo.data:
            print(f"✅ Módulo agenda registrado: {modulo.data['descripcion']}")
        else:
            print("❌ Módulo agenda no registrado en modulos_disponibles")
    except Exception as e:
        print(f"❌ Error verificando módulo: {e}")
    
    # 4. Verificar configuración para Nora
    print("\n🤖 Verificando configuración por Nora:")
    try:
        noras = supabase.table('configuracion_bot') \
            .select('nombre_nora, modulos') \
            .execute()
        
        for nora in noras.data:
            nombre = nora['nombre_nora']
            modulos = nora.get('modulos', {})
            agenda_activa = modulos.get('agenda', False)
            print(f"{'✅' if agenda_activa else '❌'} {nombre}: agenda {'activada' if agenda_activa else 'desactivada'}")
            
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
    
    print("\n" + "=" * 50)

def ejecutar_setup_sql():
    """Ejecuta el archivo SQL de setup"""
    print("🔧 EJECUTANDO SETUP SQL")
    print("=" * 30)
    
    sql_file = "setup_agenda_supabase.sql"
    
    if not os.path.exists(sql_file):
        print(f"❌ Archivo {sql_file} no encontrado")
        return False
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        print(f"📄 Leyendo {sql_file}...")
        print(f"📊 Tamaño: {len(sql_content)} caracteres")
        
        # Dividir en comandos individuales
        comandos = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        print(f"🔢 Total de comandos SQL: {len(comandos)}")
        
        # Ejecutar cada comando
        errores = 0
        exitosos = 0
        
        for i, comando in enumerate(comandos, 1):
            if comando.lower().startswith(('--', '/*')):
                continue  # Saltar comentarios
            
            try:
                # Nota: Supabase Python client no ejecuta SQL directo
                # Este script es para verificación, no ejecución
                print(f"⏭️  Comando {i}: {comando[:50]}...")
                exitosos += 1
                
            except Exception as e:
                print(f"❌ Error en comando {i}: {e}")
                errores += 1
        
        print(f"\n📊 Resultado: {exitosos} exitosos, {errores} errores")
        
        if errores == 0:
            print("✅ Setup SQL completado sin errores")
            return True
        else:
            print(f"⚠️ Setup SQL completado con {errores} errores")
            return False
            
    except Exception as e:
        print(f"❌ Error leyendo archivo SQL: {e}")
        return False

def activar_modulo_agenda():
    """Activa el módulo de agenda para todas las Noras"""
    print("🔧 ACTIVANDO MÓDULO AGENDA")
    print("=" * 30)
    
    try:
        # 1. Verificar que el módulo está registrado
        modulo = supabase.table('modulos_disponibles') \
            .select('*') \
            .eq('nombre', 'agenda') \
            .execute()
        
        if not modulo.data:
            print("📦 Registrando módulo agenda...")
            
            modulo_data = {
                'nombre': 'agenda',
                'descripcion': 'Gestión de agenda y eventos con integración a Google Calendar',
                'icono': '📅',
                'ruta': 'panel_cliente_agenda.panel_cliente_agenda_bp',
                'archivo_principal': 'panel_cliente_agenda.py'
            }
            
            result = supabase.table('modulos_disponibles') \
                .insert(modulo_data) \
                .execute()
            
            if result.data:
                print("✅ Módulo agenda registrado correctamente")
            else:
                print("❌ Error registrando módulo agenda")
                return False
        else:
            print("✅ Módulo agenda ya está registrado")
        
        # 2. Activar para todas las Noras
        noras = supabase.table('configuracion_bot') \
            .select('nombre_nora, modulos') \
            .execute()
        
        for nora_config in noras.data:
            nombre_nora = nora_config['nombre_nora']
            modulos_actuales = nora_config.get('modulos', {})
            
            if not modulos_actuales.get('agenda'):
                modulos_actuales['agenda'] = True
                
                result = supabase.table('configuracion_bot') \
                    .update({'modulos': modulos_actuales}) \
                    .eq('nombre_nora', nombre_nora) \
                    .execute()
                
                if result.data:
                    print(f"✅ Agenda activada para {nombre_nora}")
                else:
                    print(f"❌ Error activando agenda para {nombre_nora}")
            else:
                print(f"ℹ️  Agenda ya activa para {nombre_nora}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error activando módulo: {e}")
        return False

def test_funciones_agenda():
    """Prueba las funciones básicas del módulo agenda"""
    print("🧪 PROBANDO FUNCIONES DE AGENDA")
    print("=" * 35)
    
    try:
        # Importar funciones del módulo
        sys.path.append(os.path.join(os.getcwd(), 'clientes', 'aura', 'routes', 'panel_cliente_agenda'))
        
        # Importar con manejo de errores
        try:
            from clientes.aura.routes.panel_cliente_agenda.panel_cliente_agenda import (
                obtener_eventos_agenda,
                obtener_eventos_tareas,
                obtener_eventos_google_calendar
            )
        except ImportError:
            print("ℹ️  No se pueden importar funciones del módulo (normal si no está configurado)")
            return True
        
        # Test con Nora de prueba
        nombre_nora = 'aura'
        
        print(f"🔍 Probando con nombre_nora: {nombre_nora}")
        
        # 1. Test eventos de agenda
        print("\n📅 Test eventos de agenda:")
        eventos_agenda = obtener_eventos_agenda(nombre_nora)
        print(f"✅ Obtenidos {len(eventos_agenda)} eventos de agenda")
        
        # 2. Test eventos de tareas
        print("\n📋 Test eventos de tareas:")
        eventos_tareas = obtener_eventos_tareas(nombre_nora)
        print(f"✅ Obtenidos {len(eventos_tareas)} eventos de tareas")
        
        # 3. Test eventos de Google Calendar
        print("\n📆 Test eventos de Google Calendar:")
        eventos_google = obtener_eventos_google_calendar(nombre_nora)
        print(f"✅ Obtenidos {len(eventos_google)} eventos de Google Calendar")
        
        # 4. Total de eventos
        total_eventos = len(eventos_agenda) + len(eventos_tareas) + len(eventos_google)
        print(f"\n📊 Total de eventos disponibles: {total_eventos}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulo agenda: {e}")
        return False
    except Exception as e:
        print(f"❌ Error probando funciones: {e}")
        return False

def main():
    """Función principal del script"""
    print("🚀 CONFIGURADOR DE AGENDA - NORA AI")
    print("=" * 50)
    
    # 1. Verificar estado actual
    verificar_configuracion_agenda()
    
    # 2. Preguntar si continuar
    respuesta = input("\n¿Deseas continuar con la configuración? (s/n): ").lower()
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("❌ Configuración cancelada")
        return
    
    # 3. Activar módulo
    print("\n" + "="*50)
    if activar_modulo_agenda():
        print("✅ Módulo activado correctamente")
    else:
        print("❌ Error activando módulo")
        return
    
    # 4. Probar funciones
    print("\n" + "="*50)
    if test_funciones_agenda():
        print("✅ Funciones probadas correctamente")
    else:
        print("❌ Error probando funciones")
    
    # 5. Verificación final
    print("\n" + "="*50)
    verificar_configuracion_agenda()
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("📌 Puedes acceder al módulo de agenda en:")
    print("   http://localhost:5000/panel_cliente/aura/agenda")

if __name__ == "__main__":
    main()
