#!/usr/bin/env python3
"""
🔐 Script para verificar que los endpoints principales requieren autenticación
y que los endpoints temporales NO la requieren.
"""

import requests
import json

BASE_URL = "http://localhost:5000"
NOMBRE_NORA = "test"

def verificar_endpoint(url, metodo="GET", requiere_auth=True, data=None):
    """Verificar si un endpoint requiere autenticación"""
    print(f"\n🔍 Verificando {metodo} {url}")
    print(f"   Debería requerir autenticación: {'Sí' if requiere_auth else 'No'}")
    
    try:
        if metodo == "GET":
            response = requests.get(url, allow_redirects=False)
        elif metodo == "POST":
            if data:
                if isinstance(data, dict) and 'json' in str(type(data)).lower():
                    response = requests.post(url, json=data, allow_redirects=False)
                else:
                    response = requests.post(url, data=data, allow_redirects=False)
            else:
                response = requests.post(url, data={}, allow_redirects=False)
        elif metodo == "DELETE":
            response = requests.delete(url, allow_redirects=False)
        
        print(f"   Status Code: {response.status_code}")
        
        if requiere_auth:
            if response.status_code == 302:  # Redirect a login
                location = response.headers.get('Location', '')
                if '/login' in location:
                    print("   ✅ Correctamente redirige a login (requiere autenticación)")
                    return True
                else:
                    print(f"   ❌ Redirige a {location} pero debería ser a login")
                    return False
            else:
                print("   ❌ No redirige a login cuando debería requerir autenticación")
                return False
        else:
            if response.status_code in [200, 404, 500]:  # No redirect
                print("   ✅ Correctamente NO requiere autenticación")
                return True
            elif response.status_code == 302:
                print("   ❌ Redirige cuando NO debería requerir autenticación")
                return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🔐 VERIFICACIÓN DE AUTENTICACIÓN DE ENDPOINTS")
    print("=" * 60)
    
    # Endpoints que DEBEN requerir autenticación
    endpoints_con_auth = [
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar", "GET"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/personalidad", "POST"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/instrucciones", "POST"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/estado_ia", "POST"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/bloques", "GET"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/bloques", "POST"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/bloques/test-id", "DELETE"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/limites", "POST"),
        (f"/panel_cliente/{NOMBRE_NORA}/entrenar/bienvenida", "POST"),
    ]
    
    # Endpoints que NO deben requerir autenticación (temporales)
    endpoints_sin_auth = [
        (f"/test/bloques/{NOMBRE_NORA}", "GET"),
        (f"/entrenar/{NOMBRE_NORA}", "GET"),
        (f"/dev/entrenar/{NOMBRE_NORA}", "GET"),
    ]
    
    print("\n🔒 VERIFICANDO ENDPOINTS QUE REQUIEREN AUTENTICACIÓN:")
    resultados_auth = []
    for url, metodo in endpoints_con_auth:
        full_url = BASE_URL + url
        resultado = verificar_endpoint(full_url, metodo, requiere_auth=True)
        resultados_auth.append((url, metodo, resultado))
    
    print("\n🔓 VERIFICANDO ENDPOINTS QUE NO REQUIEREN AUTENTICACIÓN (TEMPORALES):")
    resultados_sin_auth = []
    for url, metodo in endpoints_sin_auth:
        full_url = BASE_URL + url
        resultado = verificar_endpoint(full_url, metodo, requiere_auth=False)
        resultados_sin_auth.append((url, metodo, resultado))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    print("\n🔒 Endpoints con autenticación:")
    auth_ok = 0
    for url, metodo, resultado in resultados_auth:
        status = "✅" if resultado else "❌"
        print(f"   {status} {metodo} {url}")
        if resultado:
            auth_ok += 1
    
    print(f"\n   Total: {auth_ok}/{len(resultados_auth)} correctos")
    
    print("\n🔓 Endpoints sin autenticación (temporales):")
    sin_auth_ok = 0
    for url, metodo, resultado in resultados_sin_auth:
        status = "✅" if resultado else "❌"
        print(f"   {status} {metodo} {url}")
        if resultado:
            sin_auth_ok += 1
    
    print(f"\n   Total: {sin_auth_ok}/{len(resultados_sin_auth)} correctos")
    
    total_correctos = auth_ok + sin_auth_ok
    total_endpoints = len(resultados_auth) + len(resultados_sin_auth)
    
    print(f"\n🎯 RESULTADO FINAL: {total_correctos}/{total_endpoints} endpoints correctamente configurados")
    
    if total_correctos == total_endpoints:
        print("\n🎉 ¡TODOS LOS ENDPOINTS ESTÁN CORRECTAMENTE CONFIGURADOS!")
    else:
        print("\n⚠️  Algunos endpoints necesitan corrección.")
    
    print("\n⚠️  RECORDATORIO: Los endpoints temporales deben ser eliminados antes de producción:")
    for url, metodo, _ in resultados_sin_auth:
        print(f"   - {metodo} {url}")

if __name__ == "__main__":
    main()
