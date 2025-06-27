#!/usr/bin/env python3
"""
🔍 Verificación DIRECTA de base de datos (sin servidor Flask)
Ejecutar este script para verificar si el problema está en la base de datos o en el frontend
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    from supabase import create_client
except ImportError as e:
    print(f"❌ Error importando librerías: {e}")
    print("💡 Instalar con: pip install python-dotenv supabase")
    sys.exit(1)

# Cargar variables de entorno
load_dotenv()

def main():
    print("🔍 VERIFICACIÓN DIRECTA DE BASE DE DATOS")
    print("=" * 50)
    
    # 1. Verificar variables de entorno
    print("1️⃣ Verificando variables de entorno...")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL:
        print("❌ SUPABASE_URL no encontrada en variables de entorno")
        return False
    else:
        print(f"✅ SUPABASE_URL: {SUPABASE_URL[:30]}...")
        
    if not SUPABASE_KEY:
        print("❌ SUPABASE_KEY no encontrada en variables de entorno")
        return False
    else:
        print(f"✅ SUPABASE_KEY: {SUPABASE_KEY[:30]}...")
    
    # 2. Conectar a Supabase
    print("\n2️⃣ Conectando a Supabase...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente Supabase creado correctamente")
    except Exception as e:
        print(f"❌ Error creando cliente Supabase: {e}")
        return False
    
    # 3. Verificar tabla conocimiento_nora
    print("\n3️⃣ Verificando tabla conocimiento_nora...")
    try:
        # Consulta general
        res_all = supabase.table("conocimiento_nora").select("count", count="exact").execute()
        total_count = res_all.count if hasattr(res_all, 'count') else 0
        print(f"📊 Total de registros en conocimiento_nora: {total_count}")
        
        # Consulta específica para 'aura'
        res_aura = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", "aura").execute()
        aura_total = len(res_aura.data) if res_aura.data else 0
        print(f"🤖 Registros para 'aura': {aura_total}")
        
        # Consulta activos para 'aura'
        res_activos = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", "aura").eq("activo", True).execute()
        aura_activos = len(res_activos.data) if res_activos.data else 0
        print(f"✅ Registros ACTIVOS para 'aura': {aura_activos}")
        
        if aura_activos == 0:
            print("⚠️ NO HAY REGISTROS ACTIVOS PARA 'AURA'")
            print("💡 Esto explicaría por qué el frontend no muestra datos")
            
            if aura_total > 0:
                print(f"\n📋 Registros inactivos encontrados ({aura_total}):")
                for registro in res_aura.data[:3]:  # Mostrar primeros 3
                    print(f"   - ID: {registro.get('id', 'N/A')[:8]}...")
                    print(f"     Contenido: {registro.get('contenido', 'N/A')[:50]}...")
                    print(f"     Activo: {registro.get('activo', 'N/A')}")
            return False
        
        # 4. Mostrar algunos registros
        print(f"\n4️⃣ Mostrando primeros registros activos para 'aura':")
        for i, registro in enumerate(res_activos.data[:3], 1):
            print(f"\n   {i}. ID: {registro.get('id', 'N/A')}")
            print(f"      Contenido: {registro.get('contenido', 'N/A')}")
            print(f"      Etiquetas: {registro.get('etiquetas', [])}")
            print(f"      Prioridad: {registro.get('prioridad', False)}")
            print(f"      Fecha: {registro.get('fecha_creacion', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error consultando conocimiento_nora: {e}")
        return False
    
    # 5. Verificar configuracion_bot
    print(f"\n5️⃣ Verificando configuracion_bot para 'aura'...")
    try:
        config_res = supabase.table("configuracion_bot").select("*").eq("nombre_nora", "aura").execute()
        
        if not config_res.data:
            print("❌ NO se encontró configuración para 'aura'")
            print("💡 Esto podría causar problemas de autenticación/autorización")
            return False
        
        config = config_res.data[0]
        print("✅ Configuración encontrada:")
        print(f"   Nombre visible: {config.get('nombre_visible', 'N/A')}")
        print(f"   IA activa: {config.get('ia_activa', 'N/A')}")
        print(f"   Módulos: {config.get('modulos', [])}")
        
    except Exception as e:
        print(f"❌ Error consultando configuracion_bot: {e}")
        return False
    
    # 6. Simular endpoint
    print(f"\n6️⃣ Simulando endpoint /admin/nora/aura/entrenar/bloques...")
    try:
        # Exactamente lo que hace el endpoint real
        nombre_nora = "aura"
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).order("fecha_creacion", desc=True).execute()
        
        respuesta_simulada = {
            "success": True,
            "data": res.data
        }
        
        print(f"✅ Simulación exitosa:")
        print(f"   Success: {respuesta_simulada['success']}")
        print(f"   Data length: {len(respuesta_simulada['data'])}")
        print(f"   JSON válido: {json.dumps(respuesta_simulada, default=str)[:100]}...")
        
    except Exception as e:
        print(f"❌ Error simulando endpoint: {e}")
        return False
    
    # 7. Conclusión
    print(f"\n" + "=" * 50)
    print("🎉 VERIFICACIÓN COMPLETADA")
    print("=" * 50)
    print(f"✅ Base de datos funcionando correctamente")
    print(f"✅ {aura_activos} bloques activos para 'aura'")
    print(f"✅ Endpoint debería responder correctamente")
    
    print(f"\n🔍 SIGUIENTE PASO:")
    print(f"Si la base de datos funciona pero el frontend sigue en 'Cargando...':")
    print(f"1. 🌐 Verificar que el servidor Flask esté ejecutándose")
    print(f"2. 🔧 Abrir consola del navegador (F12) en el panel")
    print(f"3. 📡 Verificar que las llamadas AJAX se ejecuten")
    print(f"4. 🧪 Usar la página diagnostico_completo.html")
    
    print(f"\n📁 Archivos creados para diagnóstico:")
    print(f"   - diagnostico_completo.html (abrir en navegador)")
    print(f"   - Este script (verificar_db_directo.py)")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print(f"Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
