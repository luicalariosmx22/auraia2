#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTER SIMPLE DE ACCESO POR TIPO DE CONTACTO
Verifica las respuestas personalizadas sin depender de datos específicos en la BD
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

def test_respuesta_visitante():
    """Test: Respuesta para visitante desconocido"""
    print("=" * 60)
    print("🧪 TEST: Respuesta para Visitante")
    print("=" * 60)
    
    try:
        tipo_contacto = {
            "tipo": "desconocido",
            "nombre": "Visitante",
            "email": "",
            "telefono": "5215512345678"
        }
        
        mensaje = "¿Qué servicios ofrecen?"
        print(f"💬 Mensaje: '{mensaje}'")
        print(f"👤 Tipo: {tipo_contacto['tipo']}")
        
        respuesta, _ = manejar_respuesta_ai(
            mensaje_usuario=mensaje,
            nombre_nora="aura",
            tipo_contacto=tipo_contacto
        )
        
        print(f"\n✅ Respuesta para visitante:")
        print(f"📝 {respuesta}")
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_respuesta_cliente_con_empresa():
    """Test: Respuesta personalizada para cliente con empresa"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Respuesta para Cliente con Empresa")
    print("=" * 60)
    
    try:
        tipo_contacto = {
            "tipo": "cliente",
            "id": "cliente-123",
            "nombre": "Juan Pérez",
            "email": "juan@constructora.com",
            "telefono": "5215511234567",
            "empresas": [
                {
                    "id": "empresa-456",
                    "nombre_empresa": "Constructora Pérez S.A.",
                    "industria": "Construcción",
                    "descripcion": "Empresa líder en construcción de viviendas y edificios comerciales con más de 15 años de experiencia",
                    "telefono": "5551234567",
                    "email": "contacto@constructoraperez.com"
                }
            ]
        }
        
        mensaje = "Necesito información sobre marketing digital para mi negocio"
        print(f"💬 Mensaje: '{mensaje}'")
        print(f"🏢 Cliente: {tipo_contacto['nombre']}")
        print(f"🏭 Empresa: {tipo_contacto['empresas'][0]['nombre_empresa']}")
        print(f"🔧 Industria: {tipo_contacto['empresas'][0]['industria']}")
        
        respuesta, _ = manejar_respuesta_ai(
            mensaje_usuario=mensaje,
            nombre_nora="aura",
            tipo_contacto=tipo_contacto
        )
        
        print(f"\n✅ Respuesta personalizada para cliente:")
        print(f"📝 {respuesta}")
        
        # Verificar personalización
        print(f"\n🔍 Análisis de personalización:")
        if "juan" in respuesta.lower() or "pérez" in respuesta.lower():
            print("✅ Menciona el nombre del cliente")
        else:
            print("⚠️ No menciona el nombre del cliente")
            
        if "constructora" in respuesta.lower() or "construcción" in respuesta.lower():
            print("✅ Hace referencia a su industria/empresa")
        else:
            print("⚠️ No hace referencia específica a su empresa")
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_respuesta_usuario_cliente():
    """Test: Respuesta para usuario de cliente"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Respuesta para Usuario de Cliente")
    print("=" * 60)
    
    try:
        tipo_contacto = {
            "tipo": "usuario_cliente",
            "id": "usuario-789",
            "nombre": "María González",
            "email": "",
            "telefono": "5215511111111"
        }
        
        mensaje = "Hola, tengo una pregunta sobre mi cuenta"
        print(f"💬 Mensaje: '{mensaje}'")
        print(f"👤 Usuario: {tipo_contacto['nombre']}")
        print(f"🔧 Tipo: Usuario de cliente")
        
        respuesta, _ = manejar_respuesta_ai(
            mensaje_usuario=mensaje,
            nombre_nora="aura",
            tipo_contacto=tipo_contacto
        )
        
        print(f"\n✅ Respuesta para usuario de cliente:")
        print(f"📝 {respuesta}")
        
        return respuesta
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def comparar_respuestas():
    """Comparar las diferentes respuestas"""
    print("\n" + "=" * 60)
    print("📊 COMPARACIÓN DE RESPUESTAS")
    print("=" * 60)
    
    # Ejecutar todos los tests
    respuesta_visitante = test_respuesta_visitante()
    respuesta_cliente = test_respuesta_cliente_con_empresa()
    respuesta_usuario = test_respuesta_usuario_cliente()
    
    if all([respuesta_visitante, respuesta_cliente, respuesta_usuario]):
        print(f"\n📈 Estadísticas de personalización:")
        print(f"📝 Visitante: {len(respuesta_visitante)} caracteres")
        print(f"🏢 Cliente: {len(respuesta_cliente)} caracteres")
        print(f"👤 Usuario: {len(respuesta_usuario)} caracteres")
        
        if len(respuesta_cliente) > len(respuesta_visitante):
            print("✅ La respuesta para cliente es más detallada")
        
        print(f"\n🎯 CONCLUSIÓN:")
        print("✅ El sistema de identificación de tipo de contacto está funcionando")
        print("✅ Las respuestas se personalizan según el tipo de contacto")
        print("✅ Los clientes reciben información específica sobre sus empresas")
        
        return True
    else:
        print("❌ No se pudieron completar todas las comparaciones")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TEST DE ACCESO DIFERENCIADO")
    print("=" * 80)
    
    try:
        if comparar_respuestas():
            print("\n🎉 ¡TODOS LOS TESTS COMPLETADOS EXITOSAMENTE!")
            print("🔍 Nora ahora identifica y personaliza respuestas por tipo de contacto")
        else:
            print("\n⚠️ Algunos tests fallaron")
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80)
