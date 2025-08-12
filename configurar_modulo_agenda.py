#!/usr/bin/env python3
"""
Script para configurar el módulo de agenda en Nora AI
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

def configurar_modulo_agenda():
    """Configura el módulo agenda en Supabase"""
    try:
        # Conectar a Supabase
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Variables SUPABASE_URL y SUPABASE_KEY deben estar configuradas")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conectado a Supabase")
        
        # 1. Verificar si el módulo agenda existe en modulos_disponibles
        resultado_modulo = supabase.table('modulos_disponibles') \
            .select('*') \
            .eq('nombre', 'agenda') \
            .execute()
        
        if not resultado_modulo.data:
            print("📝 Creando módulo agenda en modulos_disponibles...")
            # Crear módulo agenda
            supabase.table('modulos_disponibles').insert({
                'nombre': 'agenda',
                'descripcion': 'Gestión de agenda y calendario de eventos',
                'icono': '📅',
                'ruta': 'panel_cliente_agenda.panel_cliente_agenda_bp'
            }).execute()
            print("✅ Módulo agenda creado en modulos_disponibles")
        else:
            print("✅ Módulo agenda ya existe en modulos_disponibles")
        
        # 2. Activar módulo para Nora 'aura'
        nombre_nora = 'aura'  # Por defecto, usar aura
        
        # Obtener configuración actual
        config_result = supabase.table('configuracion_bot') \
            .select('modulos') \
            .eq('nombre_nora', nombre_nora) \
            .single() \
            .execute()
        
        if config_result.data:
            modulos_actuales = config_result.data.get('modulos', {})
            
            if not modulos_actuales.get('agenda'):
                print(f"📝 Activando módulo agenda para {nombre_nora}...")
                modulos_actuales['agenda'] = True
                
                supabase.table('configuracion_bot') \
                    .update({'modulos': modulos_actuales}) \
                    .eq('nombre_nora', nombre_nora) \
                    .execute()
                
                print(f"✅ Módulo agenda activado para {nombre_nora}")
            else:
                print(f"✅ Módulo agenda ya está activo para {nombre_nora}")
        else:
            print(f"❌ No se encontró configuración para {nombre_nora}")
            return False
        
        print("\n🎉 Configuración completada!")
        print(f"📍 URL del módulo: /panel_cliente/{nombre_nora}/agenda")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando módulo agenda: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Configurando módulo de agenda...")
    exito = configurar_modulo_agenda()
    sys.exit(0 if exito else 1)
