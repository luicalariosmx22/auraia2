#!/usr/bin/env python3
"""
Test simple para verificar la función get_whatsapp_client_instance
"""

import sys
import os
sys.path.insert(0, '.')

print("🧪 Probando función get_whatsapp_client_instance...")

try:
    from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_web import get_whatsapp_client_instance
    print("✅ Función importada correctamente")
    
    print("🔄 Intentando crear cliente...")
    client = get_whatsapp_client_instance()
    print("✅ Cliente creado exitosamente")
    print(f"🔧 Tipo: {type(client)}")
    
    # Probar que no hay recursión
    print("🔄 Probando segunda llamada...")
    client2 = get_whatsapp_client_instance()
    print("✅ Segunda llamada exitosa")
    print(f"🔧 Son el mismo objeto: {client is client2}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 Función funciona correctamente!")
