#!/usr/bin/env python3
"""
🛠️ INSTRUCCIONES PARA COMPLETAR LA CONFIGURACIÓN
"""
import sys
import os

print("🛠️ COMPLETAR CONFIGURACIÓN WEBHOOKS")
print("=" * 50)

try:
    sys.path.append('.')
    sys.path.append(os.path.join(os.getcwd(), 'clientes', 'aura'))
    from utils.quick_schemas import existe, columnas
    
    if existe('logs_webhooks_meta'):
        cols = columnas('logs_webhooks_meta')
        print(f"✅ Tabla existe con {len(cols)} columnas")
        
        # Verificar si tiene los campos que necesitamos
        if 'procesado' not in cols or 'procesado_en' not in cols:
            print("\n🔧 ACCIÓN REQUERIDA:")
            print("-" * 20)
            print("1. 🌐 Abre tu panel de Supabase")
            print("2. 📋 Ve a Table Editor > logs_webhooks_meta")
            print("3. ➕ Agrega estos campos:")
            print("   📌 Nombre: procesado")
            print("      Tipo: boolean")
            print("      Default: false")
            print("      Nullable: No")
            print("")
            print("   📌 Nombre: procesado_en") 
            print("      Tipo: timestamptz")
            print("      Default: NULL")
            print("      Nullable: Yes")
            print("")
            print("4. 💾 Guarda los cambios")
            print("5. 🔄 Ejecuta: python test_simple_webhooks.py")
            
        else:
            print("✅ ¡Todos los campos necesarios existen!")
            print("🚀 Puedes ejecutar: python test_simple_webhooks.py")
    
    else:
        print("❌ Tabla logs_webhooks_meta no existe")
        print("💡 Primero crea la tabla en Supabase")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("📚 DOCUMENTACIÓN:")
print("• Opción 1: Una sola tabla (logs_webhooks_meta)")
print("• Eliminar referencias a meta_webhook_eventos")  
print("• Campos: procesado + procesado_en para control")
print("=" * 50)
