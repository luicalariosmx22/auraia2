#!/usr/bin/env python3
"""
🚀 TEMPLATE: Test ULTRA ULTRA ULTRA eficiente
Copia este archivo y modifica según necesites

⚡ Ventajas:
- Sin cargar Flask (90+ blueprints)
- Sin cargar utils de la app  
- Conexión directa a Supabase
- Resultado: < 1 segundo vs 30+ segundos

📋 Uso:
1. Copia este archivo: cp tests/template_ultra_eficiente.py tests/test_mi_funcion.py
2. Modifica las variables y la lógica según tu caso
3. Ejecuta: python tests/test_mi_funcion.py
"""

from supabase.client import create_client, Client

# 🔐 Configuración directa (sin .env)
SUPABASE_URL = "https://sylqljdiiyhtgtrghwjk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q"

def test_ultra_eficiente_template():
    """Template para test ultra eficiente - modifica según tu caso"""
    
    # Conexión directa sin Flask
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🚀 Test ULTRA eficiente iniciado")
    print("⚡ Sin blueprints, sin Flask, sin esperas")
    print("=" * 50)
    
    # 🔍 PASO 0: Verificar que la tabla existe
    TABLA_TEST = "configuracion_bot"  # ✅ Cambiar por tu tabla real
    
    try:
        print(f"🔍 Verificando que tabla '{TABLA_TEST}' existe...")
        test_table = supabase.table(TABLA_TEST).select('*').limit(1).execute()
        print(f"✅ Tabla '{TABLA_TEST}' confirmada")
    except Exception as e:
        print(f"❌ TABLA '{TABLA_TEST}' NO EXISTE: {e}")
        print("💡 Usa solo tablas reales de esta lista:")
        print("   - configuracion_bot, modulos_disponibles, facebook_paginas")
        print("   - contactos, memoria, meta_publicaciones_webhook, etc.")
        return False
    
    try:
        # 📊 PASO 1: Verificar estado actual
        print("📋 Verificando estado actual...")
        
        # Ejemplo: consultar configuracion_bot (tabla REAL)
        result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", "aura").limit(1).execute()
        
        if result.data:
            registro = result.data[0]
            print(f"✅ Registro encontrado:")
            print(f"   - Nora: {registro.get('nombre_nora')}")
            print(f"   - Módulos: {len(registro.get('modulos', {}))}")
        else:
            print("❌ No se encontró configuración para 'aura'")
            return False
        
        # 🔧 PASO 2: Realizar operación (ejemplo: actualizar timestamp)
        print(f"\n🔧 Ejecutando operación...")
        
        from datetime import datetime
        update_response = supabase.table('configuracion_bot').update({
            'updated_at': datetime.now().isoformat()
        }).eq('nombre_nora', 'aura').execute()
        
        if update_response.data:
            print("✅ Operación exitosa")
            
            # 📊 PASO 3: Verificar resultado
            final_result = supabase.table("configuracion_bot").select("updated_at").eq("nombre_nora", "aura").execute()
            if final_result.data:
                final_registro = final_result.data[0]
                print(f"📊 Estado final:")
                print(f"   - Actualizado: {final_registro.get('updated_at')}")
                return True
        else:
            print("❌ No se pudo actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_funcion_pura():
    """Ejemplo de test de función pura - sin BD"""
    
    def mi_logica_pura(estado: str, activo: bool) -> str:
        """Función pura para testear lógica sin dependencias"""
        return 'ok' if estado == 'activo' and activo else 'error'
    
    # Tests directos
    assert mi_logica_pura('activo', True) == 'ok'
    assert mi_logica_pura('inactivo', True) == 'error'
    assert mi_logica_pura('activo', False) == 'error'
    
    print("✅ Tests de función pura: PASSED")

if __name__ == "__main__":
    print("🧪 TEMPLATE: Test Ultra Eficiente")
    print("📝 Modifica este archivo según tu caso específico")
    print()
    
    # 1. Test de lógica pura (instantáneo)
    test_funcion_pura()
    
    # 2. Test con BD (ultra rápido)
    resultado = test_ultra_eficiente_template()
    
    if resultado:
        print("\n🎯 ¡Test completado exitosamente!")
        print("💡 Tiempo total: < 1 segundo")
    else:
        print("\n❌ Error en el test")
    
    print("\n🔥 RECUERDA:")
    print("   - Modifica TABLA_TEST por tu tabla real")
    print("   - Solo usar tablas verificadas que existen:")
    print("     * configuracion_bot, modulos_disponibles, facebook_paginas")
    print("     * contactos, memoria, meta_publicaciones_webhook")
    print("     * logs_webhooks_meta, google_ads_campañas, etc.")
    print("   - NO inventar nombres de tablas")
    print("   - Verificar siempre con verificar_tabla_existe()")
    print("   - Borra este archivo después de usar")
