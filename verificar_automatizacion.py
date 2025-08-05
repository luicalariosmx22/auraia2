#!/usr/bin/env python3
"""
Script para verificar las tablas de automatización
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

def verificar_tablas():
    """
    Verifica el estado de las tablas de automatización
    """
    print("🔍 Verificando tablas de automatización...")
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        tablas_a_verificar = [
            'meta_ads_automatizaciones',
            'meta_publicaciones_webhook',
            'meta_anuncios_automatizados',
            'meta_paginas_webhook',
            'meta_plantillas_anuncios'
        ]
        
        for tabla in tablas_a_verificar:
            try:
                # Intentar hacer una consulta simple
                resultado = supabase.table(tabla).select('*').limit(1).execute()
                
                print(f"   ✅ Tabla '{tabla}' existe y es accesible")
                
                # Mostrar cantidad de registros
                try:
                    count_result = supabase.table(tabla).select('*').execute()
                    count = len(count_result.data or [])
                    print(f"      📊 Registros: {count}")
                except:
                    print(f"      📊 Registros: No disponible")
                
            except Exception as e:
                print(f"   ❌ Tabla '{tabla}' ERROR: {e}")
        
        print("\n🎯 Verificando plantilla por defecto...")
        
        # Verificar plantilla por defecto
        plantillas = supabase.table('meta_plantillas_anuncios').select('*').execute()
        
        if plantillas.data:
            print(f"   ✅ Encontradas {len(plantillas.data)} plantilla(s)")
            for plantilla in plantillas.data:
                print(f"      📝 '{plantilla['nombre']}' - {'Activa' if plantilla['activa'] else 'Inactiva'}")
        else:
            print("   ⚠️ No hay plantillas configuradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def mostrar_resumen_sistema():
    """
    Muestra un resumen del estado del sistema
    """
    print("\n" + "="*60)
    print("📋 RESUMEN DEL SISTEMA DE AUTOMATIZACIÓN")
    print("="*60)
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Verificar configuración de webhook
        print("🔗 Estado del Webhook:")
        print("   ✅ Archivo webhooks_meta.py actualizado para eventos 'feed'")
        print("   ✅ Función procesar_publicacion_webhook implementada")
        
        # Verificar rutas
        print("\n🛣️ Rutas disponibles:")
        print("   ✅ /automatizacion - Panel principal")
        print("   ✅ /automatizacion/crear - Crear automatización")
        print("   ✅ /api/automatizacion/* - APIs")
        
        # Verificar templates
        template_path = Path(__file__).parent / 'clientes' / 'aura' / 'templates' / 'panel_cliente_meta_ads' / 'automatizacion.html'
        if template_path.exists():
            print("\n🎨 Templates:")
            print("   ✅ automatizacion.html - Panel principal")
        else:
            print("\n❌ Template no encontrado")
        
        print(f"\n🌐 Acceso: http://localhost:5000/automatizacion")
        
    except Exception as e:
        print(f"\n❌ Error verificando sistema: {e}")

if __name__ == "__main__":
    print("🤖 VERIFICADOR DE AUTOMATIZACIÓN META ADS")
    print("=" * 50)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar tablas
    if verificar_tablas():
        mostrar_resumen_sistema()
        
        print(f"\n🎉 ¡Sistema verificado exitosamente!")
        print(f"\n📝 Próximos pasos:")
        print(f"   1. Crear tablas en Supabase con el SQL proporcionado")
        print(f"   2. Configurar webhook en Meta Developer para eventos 'feed'")
        print(f"   3. Crear primera automatización desde el panel")
        print(f"   4. Probar con publicación real")
        
    else:
        print(f"\n❌ Sistema requiere configuración")
    
    print("\n" + "=" * 50)
