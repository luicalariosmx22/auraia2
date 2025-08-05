"""
Diagnóstico: Ver qué nombre_nora tienes en tus alertas actuales
"""

import sys
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase

def ver_nombres_nora():
    """Ver todos los nombre_nora que existen en las alertas"""
    try:
        print("🔍 Buscando nombres de Nora en la base de datos...")
        
        # Obtener todos los nombre_nora únicos de las alertas
        response = supabase.table("alertas") \
            .select("nombre_nora") \
            .execute()
        
        if response.data:
            nombres_unicos = list(set([alerta['nombre_nora'] for alerta in response.data if alerta['nombre_nora']]))
            
            print(f"\n📋 Nombres de Nora encontrados ({len(nombres_unicos)}):")
            for i, nombre in enumerate(nombres_unicos, 1):
                print(f"  {i}. '{nombre}'")
                
            print(f"\n💡 Usa uno de estos nombres en el script de configuración")
            return nombres_unicos
        else:
            print("❌ No se encontraron alertas en la base de datos")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def ver_configuraciones_existentes():
    """Ver qué configuraciones ya existen"""
    try:
        print("\n🔍 Buscando configuraciones existentes...")
        
        response = supabase.table("configuracion_notificaciones") \
            .select("*") \
            .execute()
        
        if response.data:
            print(f"\n📋 Configuraciones encontradas ({len(response.data)}):")
            for config in response.data:
                print(f"  👤 {config['nombre_nora']} - 📧 {config['email']} - Email: {'✅' if config['email_notificaciones'] else '❌'}")
        else:
            print("❌ No hay configuraciones de notificaciones")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO DE CONFIGURACIÓN")
    print("=" * 40)
    
    nombres = ver_nombres_nora()
    ver_configuraciones_existentes()
    
    if nombres:
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"1. Edita configurar_notificaciones_rapido.py")
        print(f"2. Cambia NOMBRE_NORA = '{nombres[0]}'  # (o el que prefieras)")
        print(f"3. Cambia EMAIL_DESTINO = 'tu_email_real@ejemplo.com'")
        print(f"4. Ejecuta el script para configurar notificaciones")
