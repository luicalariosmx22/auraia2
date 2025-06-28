#!/usr/bin/env python3
"""
🧪 Prueba Rápida del Endpoint de Conocimiento
Verifica que el endpoint funcione desde el contexto correcto
"""

import requests
import json
from datetime import datetime

def probar_endpoint_conocimiento():
    """Prueba el endpoint de conocimiento"""
    print("🧪 PROBANDO ENDPOINT DE CONOCIMIENTO")
    print("=" * 50)
    
    # URLs a probar
    urls_a_probar = [
        "http://localhost:5000/panel_cliente/aura/entrenar/bloques",
        "http://127.0.0.1:5000/panel_cliente/aura/entrenar/bloques",
        "http://localhost:5000/admin/nora/aura/entrenar/bloques",
        "http://127.0.0.1:5000/admin/nora/aura/entrenar/bloques"
    ]
    
    for url in urls_a_probar:
        print(f"\n🔗 Probando: {url}")
        print("-" * 40)
        
        try:
            response = requests.get(url, timeout=10)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON válido recibido")
                    print(f"📦 Success: {data.get('success', 'N/A')}")
                    print(f"📦 Total bloques: {len(data.get('data', []))}")
                    
                    if data.get('data'):
                        print(f"📋 Primer bloque:")
                        primer_bloque = data['data'][0]
                        print(f"   ID: {primer_bloque.get('id', 'N/A')[:8]}...")
                        print(f"   Contenido: {primer_bloque.get('contenido', 'N/A')[:50]}...")
                        print(f"   Etiquetas: {primer_bloque.get('etiquetas', [])}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Respuesta no es JSON válido")
                    print(f"📄 Contenido: {response.text[:200]}...")
                    
            elif response.status_code == 302:
                print(f"🔄 Redirección a: {response.headers.get('Location', 'N/A')}")
                print(f"⚠️ Posible problema de autenticación")
                
            elif response.status_code == 404:
                print(f"❌ Endpoint no encontrado")
                
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"📄 Contenido: {response.text[:200]}...")
                
        except requests.exceptions.ConnectRefused:
            print(f"❌ Conexión rechazada - servidor no está corriendo")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout - servidor no responde")
        except Exception as e:
            print(f"❌ Error: {e}")

def probar_datos_supabase():
    """Prueba directa a Supabase"""
    print(f"\n🗃️ PROBANDO DATOS EN SUPABASE")
    print("=" * 50)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from clientes.aura.utils.supabase_client import supabase
        
        # Consulta directa
        response = supabase.table("conocimiento_nora") \
            .select("*") \
            .eq("nombre_nora", "aura") \
            .eq("activo", True) \
            .order("fecha_creacion", desc=True) \
            .execute()
        
        print(f"✅ Consulta Supabase exitosa")
        print(f"📊 Total bloques: {len(response.data)}")
        
        for i, bloque in enumerate(response.data, 1):
            print(f"\n📋 Bloque {i}:")
            print(f"   ID: {bloque['id'][:8]}...")
            print(f"   Contenido: {bloque['contenido'][:50]}...")
            print(f"   Etiquetas: {bloque['etiquetas']}")
            print(f"   Prioridad: {bloque['prioridad']}")
            print(f"   Activo: {bloque['activo']}")
            
    except Exception as e:
        print(f"❌ Error consultando Supabase: {e}")

def main():
    """Función principal"""
    print(f"🚀 DIAGNÓSTICO COMPLETO DE CONOCIMIENTO")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    probar_datos_supabase()
    probar_endpoint_conocimiento()
    
    print(f"\n🎉 DIAGNÓSTICO COMPLETADO")
    print("=" * 70)
    
    print(f"\n💡 PASOS SIGUIENTES:")
    print(f"   1. Abre el navegador en http://localhost:5000")
    print(f"   2. Ve a Panel Cliente > Entrenar Nora")
    print(f"   3. Abre la consola del navegador (F12)")
    print(f"   4. Busca errores en la consola")
    print(f"   5. También puedes abrir diagnostico_conocimiento.html")

if __name__ == "__main__":
    main()
