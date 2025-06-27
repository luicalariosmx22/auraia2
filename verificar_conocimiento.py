#!/usr/bin/env python3
"""
🔍 Verificación directa de la base de conocimiento
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def verificar_conocimiento():
    """Verificar directamente la tabla conocimiento_nora"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Variables de entorno no configuradas")
        print(f"SUPABASE_URL: {'✅' if SUPABASE_URL else '❌'}")
        print(f"SUPABASE_KEY: {'✅' if SUPABASE_KEY else '❌'}")
        return False

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔍 Verificando conexión a Supabase...")
        
        # Consultar conocimiento para 'aura'
        print("\n📋 Consultando conocimiento_nora para 'aura'...")
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", "aura").eq("activo", True).execute()
        
        print(f"✅ Consulta exitosa - {len(res.data)} bloques encontrados")
        
        if res.data:
            print("\n📄 Bloques encontrados:")
            for i, bloque in enumerate(res.data[:3], 1):  # Mostrar solo los primeros 3
                print(f"\n{i}. ID: {bloque.get('id', 'N/A')[:8]}...")
                print(f"   Contenido: {bloque.get('contenido', 'N/A')[:60]}...")
                print(f"   Etiquetas: {bloque.get('etiquetas', [])}")
                print(f"   Prioridad: {bloque.get('prioridad', False)}")
                print(f"   Activo: {bloque.get('activo', False)}")
        else:
            print("⚠️ No se encontraron bloques para 'aura'")
            
        # Verificar configuración de bot
        print("\n🤖 Verificando configuracion_bot para 'aura'...")
        config_res = supabase.table("configuracion_bot").select("*").eq("nombre_nora", "aura").execute()
        
        if config_res.data:
            config = config_res.data[0]
            print("✅ Configuración encontrada:")
            print(f"   Nombre visible: {config.get('nombre_visible', 'N/A')}")
            print(f"   IA activa: {config.get('ia_activa', 'N/A')}")
            print(f"   Módulos: {config.get('modulos', [])}")
        else:
            print("❌ No se encontró configuración para 'aura'")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        return False

def simular_endpoint():
    """Simular exactamente lo que hace el endpoint"""
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("\n🔧 Simulando endpoint /admin/nora/aura/entrenar/bloques...")
        
        # Esto es exactamente lo que hace el endpoint
        nombre_nora = "aura"
        print(f"🔍 Buscando bloques para: {nombre_nora}")
        
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).order("fecha_creacion", desc=True).execute()
        
        print(f"✅ Resultado consulta: {len(res.data)} bloques encontrados")
        print(f"📄 Datos: {res.data}")
        
        # Simular respuesta JSON
        respuesta = {"success": True, "data": res.data}
        print(f"\n📡 Respuesta que debería enviar el endpoint:")
        print(f"Success: {respuesta['success']}")
        print(f"Data length: {len(respuesta['data'])}")
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error simulando endpoint: {e}")
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    print("🧪 VERIFICACIÓN DIRECTA DE BASE DE CONOCIMIENTO")
    print("=" * 50)
    
    if verificar_conocimiento():
        print("\n" + "="*50)
        simular_endpoint()
        
        print("\n" + "="*50)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("\n🔧 Si los datos se muestran aquí pero no en el frontend:")
        print("   1. El problema está en el frontend/JavaScript")
        print("   2. Verificar consola del navegador (F12)")
        print("   3. Verificar que el servidor Flask esté ejecutándose")
        print("   4. Verificar que la URL del endpoint sea correcta")
        
        print(f"\n🌐 URLs para probar:")
        print(f"   Frontend: http://localhost:5000/admin/nora/aura/entrenar")
        print(f"   API: http://localhost:5000/admin/nora/aura/entrenar/bloques")
    else:
        print("\n❌ HAY PROBLEMAS DE CONEXIÓN A LA BASE DE DATOS")
        print("   Verificar variables de entorno y conexión a Supabase")
