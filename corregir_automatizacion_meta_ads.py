#!/usr/bin/env python3
"""
Script para corregir la configuración de automatizaciones
Actualiza el módulo de sincronización de reportes Meta Ads
"""

import sys
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase

def corregir_automatizacion_meta_ads():
    print("🔧 Corrigiendo configuración de automatización Meta Ads...")
    
    try:
        # Buscar la automatización de reportes semanales
        result = supabase.table('automatizaciones') \
            .select('*') \
            .ilike('nombre', '%Meta Ads - Reportes Semanales%') \
            .execute()
        
        if not result.data:
            print("❌ No se encontró la automatización 'Meta Ads - Reportes Semanales'")
            return False
        
        automatizacion = result.data[0]
        print(f"✅ Encontrada automatización:")
        print(f"   ID: {automatizacion['id']}")
        print(f"   Nombre: {automatizacion['nombre']}")
        print(f"   Módulo actual: {automatizacion.get('modulo_relacionado', 'N/A')}")
        print(f"   Función actual: {automatizacion.get('funcion_objetivo', 'N/A')}")
        
        # Actualizar la configuración
        update_data = {
            'modulo_relacionado': 'sincronizador_semanal',
            'funcion_objetivo': 'sincronizar_reportes_semanales',
            'actualizado_en': 'now()'
        }
        
        update_result = supabase.table('automatizaciones') \
            .update(update_data) \
            .eq('id', automatizacion['id']) \
            .execute()
        
        if update_result.data:
            print("\n✅ Automatización actualizada correctamente:")
            print(f"   Nuevo módulo: {update_data['modulo_relacionado']}")
            print(f"   Nueva función: {update_data['funcion_objetivo']}")
            return True
        else:
            print("❌ Error al actualizar la automatización")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_funcion_disponible():
    print("\n🔍 Verificando que la función esté disponible...")
    
    try:
        from clientes.aura.routes.panel_cliente_meta_ads.sincronizador_semanal import sincronizar_reportes_semanales
        print("✅ Función 'sincronizar_reportes_semanales' importada correctamente")
        
        # Verificar también el módulo en el ejecutor
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        if 'sincronizador_semanal' in ejecutor.modulos_disponibles:
            print("✅ Módulo 'sincronizador_semanal' registrado en el ejecutor")
            return True
        else:
            print("❌ Módulo 'sincronizador_semanal' NO registrado en el ejecutor")
            return False
            
    except ImportError as e:
        print(f"❌ Error al importar la función: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando corrección de automatización Meta Ads...")
    print("=" * 60)
    
    # Verificar función disponible
    if not verificar_funcion_disponible():
        print("❌ La función no está disponible. Abortando.")
        sys.exit(1)
    
    # Corregir configuración
    if corregir_automatizacion_meta_ads():
        print("\n🎉 ¡Corrección completada exitosamente!")
        print("\n💡 Ahora puedes ejecutar:")
        print("   python ejecutar_automatizaciones.py --todas --verbose")
    else:
        print("\n❌ La corrección falló")
        sys.exit(1)
    
    print("=" * 60)
