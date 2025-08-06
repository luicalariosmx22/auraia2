#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script ejecutor rápido para suscribir webhooks en todas las páginas de Facebook
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from suscribir_webhooks_facebook_pages import suscribir_webhooks_masivo

def main():
    """
    Ejecuta directamente la suscripción masiva de webhooks
    """
    print("🚀 SUSCRIPCIÓN MASIVA AUTOMÁTICA DE WEBHOOKS")
    print("=" * 60)
    print("Iniciando proceso de suscripción para todas las páginas...")
    print()
    
    # Ejecutar suscripción masiva
    resultado = suscribir_webhooks_masivo()
    
    if 'error' in resultado:
        print(f"\n❌ ERROR: {resultado['error']}")
        print("💡 Verifica tu configuración:")
        print("   - META_ACCESS_TOKEN")
        print("   - META_WEBHOOK_URL")
        print("   - META_WEBHOOK_VERIFY_TOKEN")
        return False
    
    # Mostrar resumen
    print(f"\n🎉 PROCESO COMPLETADO EXITOSAMENTE!")
    print(f"✅ Páginas suscritas: {resultado.get('exitosos', 0)}")
    print(f"🔄 Ya suscritas: {resultado.get('ya_suscritos', 0)}")
    print(f"❌ Fallidas: {resultado.get('fallidos', 0)}")
    print(f"📊 Total procesadas: {resultado.get('total', 0)}")
    
    fallidos = resultado.get('fallidos', 0)
    if isinstance(fallidos, int) and fallidos > 0:
        print(f"\n⚠️ Hay {fallidos} páginas que fallaron.")
        print("💡 Ejecuta el script completo para ver detalles de los errores:")
        print("   python suscribir_webhooks_facebook_pages.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ Script completado exitosamente")
    else:
        print(f"\n❌ Script falló")
        sys.exit(1)
