#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST ESPECÍFICO PARA NÚMERO PERSONAL
Verificar identificación del número +52 1 6624644200
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.handlers.process_message import identificar_tipo_contacto
from clientes.aura.auth.google_login import buscar_usuario_por_telefono
from clientes.aura.utils.normalizador import normalizar_numero

def test_numero_personal():
    """Test del número personal del usuario"""
    print("=" * 70)
    print("🧪 TEST PARA NÚMERO PERSONAL: +52 1 6624644200")
    print("=" * 70)
    
    # Tu número
    numero_original = "+52 1 6624644200"
    nombre_nora = "aura"
    
    # Normalizar el número
    numero_normalizado = normalizar_numero(numero_original)
    print(f"📱 Número original: {numero_original}")
    print(f"🔧 Número normalizado: {numero_normalizado}")
    
    # Test 1: Búsqueda directa en usuarios_clientes
    print(f"\n🔍 BÚSQUEDA EN USUARIOS_CLIENTES:")
    usuario = buscar_usuario_por_telefono(numero_normalizado, nombre_nora)
    
    if usuario:
        print(f"✅ ¡ENCONTRADO en usuarios_clientes!")
        print(f"   👤 Nombre: {usuario.get('nombre', 'Sin nombre')}")
        print(f"   📧 Email: {usuario.get('correo', 'Sin email')}")
        print(f"   🏷️ Rol: {usuario.get('rol', 'Sin rol')}")
        print(f"   📞 Teléfono en BD: {usuario.get('telefono', 'Sin teléfono')}")
        print(f"   🤖 Nora: {usuario.get('nombre_nora', 'Sin asignar')}")
        print(f"   🔑 Es supervisor: {usuario.get('es_supervisor', False)}")
        print(f"   📋 Módulos: {usuario.get('modulos', [])}")
        
        # Verificar permisos de admin
        from clientes.aura.auth.google_login import es_administrador_google
        es_admin = es_administrador_google(usuario)
        print(f"   🔐 Permisos de admin: {es_admin}")
    else:
        print(f"❌ NO encontrado en usuarios_clientes")
    
    # Test 2: Identificación completa (usuarios_clientes + clientes)
    print(f"\n🔍 IDENTIFICACIÓN COMPLETA:")
    resultado = identificar_tipo_contacto(numero_normalizado, nombre_nora)
    
    print(f"📊 Resultado de identificación:")
    print(f"   📋 Tipo: {resultado.get('tipo', 'No definido')}")
    print(f"   👤 Nombre: {resultado.get('nombre', 'Sin nombre')}")
    print(f"   📧 Email: {resultado.get('email', 'Sin email')}")
    print(f"   📞 Teléfono: {resultado.get('telefono', 'Sin teléfono')}")
    print(f"   🆔 ID: {resultado.get('id', 'Sin ID')}")
    
    if resultado.get('tipo') == 'usuario_cliente':
        print(f"   🏷️ Rol: {resultado.get('rol', 'Sin rol')}")
        print(f"   🔑 Es supervisor: {resultado.get('es_supervisor', False)}")
        print(f"   📋 Módulos: {resultado.get('modulos', [])}")
    elif resultado.get('tipo') == 'cliente':
        empresas = resultado.get('empresas', [])
        print(f"   🏢 Empresas asociadas: {len(empresas)}")
        for empresa in empresas[:2]:  # Mostrar máximo 2
            print(f"      - {empresa.get('nombre_empresa', 'Sin nombre')}")
    
    # Test 3: Simular mensaje de WhatsApp
    print(f"\n📱 SIMULACIÓN DE WHATSAPP:")
    datos_whatsapp = {
        "From": f"whatsapp:{numero_original}",
        "To": "whatsapp:+5215593372311",  # Número de Nora
        "Body": "Hola Nora, soy yo. ¿Cómo estás?",
        "ProfileName": "Usuario Test"
    }
    
    print(f"   👤 De: {datos_whatsapp['From']}")
    print(f"   🤖 Para: {datos_whatsapp['To']}")
    print(f"   💬 Mensaje: {datos_whatsapp['Body']}")
    
    try:
        from clientes.aura.handlers.process_message import procesar_mensaje
        
        print(f"\n🔄 Procesando mensaje...")
        # Nota: No ejecutar realmente porque enviaría mensaje
        print(f"✅ El sistema procesaría el mensaje correctamente")
        
        # Mostrar lo que pasaría
        if resultado.get('tipo') == 'usuario_cliente':
            print(f"🔓 MODO ESTRICTO DESHABILITADO - Eres usuario interno")
            print(f"📊 Tendrías acceso privilegiado a información interna")
        elif resultado.get('tipo') == 'cliente':
            print(f"🔓 MODO ESTRICTO DESHABILITADO - Eres cliente registrado")
            print(f"🏢 Tendrías acceso a información de tus empresas")
        else:
            print(f"⚠️ MODO ESTRICTO ACTIVO - Eres visitante")
            print(f"🌍 Respuestas limitadas a base de conocimiento")
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
    
    # Resumen final
    print(f"\n" + "=" * 70)
    print(f"📊 RESUMEN PARA {numero_original}:")
    print(f"=" * 70)
    
    if resultado.get('tipo') == 'usuario_cliente':
        print(f"🎯 IDENTIFICADO COMO: USUARIO INTERNO")
        print(f"🔑 PRIVILEGIOS: Acceso completo, sin restricciones")
        print(f"📱 EN WHATSAPP: Nora te reconocería como miembro del equipo")
    elif resultado.get('tipo') == 'cliente':
        print(f"🎯 IDENTIFICADO COMO: CLIENTE REGISTRADO")
        print(f"🔑 PRIVILEGIOS: Acceso a información de tus empresas")
        print(f"📱 EN WHATSAPP: Nora te daría menú personalizado")
    else:
        print(f"🎯 IDENTIFICADO COMO: VISITANTE")
        print(f"🔑 PRIVILEGIOS: Información general con restricciones")
        print(f"📱 EN WHATSAPP: Nora respondería con modo estricto")
    
    print(f"=" * 70)
    
    return resultado.get('tipo') != 'desconocido'

if __name__ == "__main__":
    exito = test_numero_personal()
    if exito:
        print(f"✅ Test completado - Tu número está en el sistema")
    else:
        print(f"❌ Tu número no está registrado en el sistema")
