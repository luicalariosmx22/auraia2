"""
Script de prueba para la funcionalidad de compartir reportes Meta Ads
"""

import requests
import json
from datetime import datetime

def probar_compartir_reporte():
    """Prueba la funcionalidad de generar enlaces públicos para reportes"""
    
    # URL base (ajustar según tu configuración)
    base_url = "http://localhost:5000"  # Cambiar por tu URL
    
    # Datos de prueba
    datos_prueba = {
        "reporte_id": 1,  # Cambiar por un ID real de reporte
        "empresa_nombre": "Empresa Test",
        "periodo": "2024-01-01 - 2024-01-07",
        "nombre_nora": "admin"
    }
    
    print("🧪 Probando funcionalidad de compartir reportes...")
    print(f"📊 Datos de prueba: {datos_prueba}")
    
    try:
        # Hacer petición para generar enlace
        response = requests.post(
            f"{base_url}/panel_cliente/admin/meta_ads/estadisticas/compartir_reporte",
            json=datos_prueba,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enlace generado exitosamente!")
            print(f"🔗 URL pública: {data.get('url_publico')}")
            print(f"🔑 Token UUID: {data.get('token_uuid')}")
            print(f"🔐 Token seguridad: {data.get('token')}")
            
            # Probar el enlace público
            url_publico = data.get('url_publico')
            if url_publico:
                print(f"\n🌐 Probando acceso al enlace público...")
                response_publico = requests.get(url_publico)
                print(f"📈 Status del enlace público: {response_publico.status_code}")
                
                if response_publico.status_code == 200:
                    print("✅ Enlace público funciona correctamente!")
                else:
                    print(f"❌ Error al acceder al enlace público: {response_publico.text}")
        else:
            print(f"❌ Error al generar enlace: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el servidor Flask?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def probar_validacion_enlace():
    """Prueba la API de validación de enlaces"""
    
    base_url = "http://localhost:5000"
    token_uuid = "26b976fe-2776-4454-84d4-6cd27d2a7487"  # UUID de ejemplo
    token_seguridad = "b578445791a1931bde6766cb2c18ca0e"  # Token de ejemplo
    
    print(f"\n🔍 Probando validación de enlace...")
    print(f"🆔 Token UUID: {token_uuid}")
    print(f"🔐 Token seguridad: {token_seguridad}")
    
    try:
        response = requests.get(
            f"{base_url}/panel_cliente/admin/meta_ads/api/reporte_publico/{token_uuid}/validar",
            params={'token': token_seguridad}
        )
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Validación exitosa!")
            print(f"📊 Datos: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error en validación: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en validación: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de compartir reportes Meta Ads...")
    print("=" * 60)
    
    probar_compartir_reporte()
    probar_validacion_enlace()
    
    print("\n" + "=" * 60)
    print("✨ Pruebas completadas!")
    
    print("""
📋 Instrucciones para usar la funcionalidad:

1. 🔗 Generar enlace público:
   POST /panel_cliente/{nombre_nora}/meta_ads/estadisticas/compartir_reporte
   Body: {
     "reporte_id": 123,
     "empresa_nombre": "Mi Empresa",
     "periodo": "2024-01-01 - 2024-01-07",
     "nombre_nora": "admin"
   }

2. 🌐 Acceder al reporte público:
   GET /panel_cliente/{nombre_nora}/meta_ads/reporte_publico/{token_uuid}?token={token_seguridad}

3. ✅ Validar enlace:
   GET /panel_cliente/{nombre_nora}/meta_ads/api/reporte_publico/{token_uuid}/validar?token={token_seguridad}

🗄️ Tabla requerida en Supabase:
   - Ejecutar el script: meta_ads_reportes_compartidos.sql
    """)
