#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test específico para verificar la identificación del número +52 1 6624644200
Este es el número personal del usuario para confirmar que el sistema
de identificación funciona correctamente.
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from clientes.aura.auth.google_login import buscar_usuario_por_telefono
from clientes.aura.handlers.process_message import identificar_tipo_contacto
from clientes.aura.utils.normalizador import normalizar_numero

def test_mi_numero_celular():
    """
    Test del número personal +52 1 6624644200
    """
    print("=" * 60)
    print("🧪 TEST: MI NÚMERO CELULAR +52 1 6624644200")
    print("=" * 60)
    
    # El número a testear
    mi_numero = "+52 1 6624644200"
    nombre_nora = "aura"  # Asumiendo que usas "aura"
    
    print(f"📱 Número a testear: {mi_numero}")
    print(f"🤖 Nombre Nora: {nombre_nora}")
    print()
    
    # Test 1: Normalización del número
    print("1️⃣ TEST NORMALIZACIÓN:")
    numero_normalizado = normalizar_numero(mi_numero)
    print(f"   Original: {mi_numero}")
    print(f"   Normalizado: {numero_normalizado}")
    print()
    
    # Test 2: Búsqueda directa por teléfono en usuarios_clientes
    print("2️⃣ TEST BÚSQUEDA EN usuarios_clientes:")
    usuario_encontrado = buscar_usuario_por_telefono(mi_numero, nombre_nora)
    
    if usuario_encontrado:
        print(f"   ✅ ENCONTRADO en usuarios_clientes!")
        print(f"   👤 Nombre: {usuario_encontrado.get('nombre', 'Sin nombre')}")
        print(f"   📧 Email: {usuario_encontrado.get('correo', 'Sin email')}")
        print(f"   🏷️ Rol: {usuario_encontrado.get('rol', 'Sin rol')}")
        print(f"   📞 Teléfono BD: {usuario_encontrado.get('telefono', 'Sin teléfono')}")
        print(f"   🆔 ID: {usuario_encontrado.get('id', 'Sin ID')}")
        print(f"   ⚡ Activo: {usuario_encontrado.get('activo', 'Sin estado')}")
    else:
        print("   ❌ NO ENCONTRADO en usuarios_clientes")
    print()
    
    # Test 3: Identificación completa del contacto (WhatsApp flow)
    print("3️⃣ TEST IDENTIFICACIÓN COMPLETA (WhatsApp):")
    tipo_contacto = identificar_tipo_contacto(mi_numero, nombre_nora)
    
    print(f"   📋 Resultado identificación:")
    print(f"   - Tipo: {tipo_contacto.get('tipo', 'Sin tipo')}")
    print(f"   - Nombre: {tipo_contacto.get('nombre', 'Sin nombre')}")
    print(f"   - Email: {tipo_contacto.get('email', 'Sin email')}")
    print(f"   - ID: {tipo_contacto.get('id', 'Sin ID')}")
    print(f"   - Es Admin: {tipo_contacto.get('es_admin', False)}")
    print()
    
    # Test 4: Verificación de privilegios
    print("4️⃣ TEST PRIVILEGIOS:")
    if usuario_encontrado:
        from clientes.aura.auth.google_login import es_administrador_google
        es_admin = es_administrador_google(usuario_encontrado)
        print(f"   🔑 Es administrador: {es_admin}")
        
        # Mostrar detalles de privilegios
        print(f"   📊 Detalles privilegios:")
        print(f"   - Rol: {usuario_encontrado.get('rol', 'Sin rol')}")
        print(f"   - Es supervisor: {usuario_encontrado.get('es_supervisor', False)}")
        print(f"   - Es supervisor tareas: {usuario_encontrado.get('es_supervisor_tareas', False)}")
        print(f"   - Módulos: {usuario_encontrado.get('modulos', 'Sin módulos')}")
    else:
        print("   ❌ No se pueden verificar privilegios (usuario no encontrado)")
    print()
    
    # Test 5: Variaciones del número
    print("5️⃣ TEST VARIACIONES DEL NÚMERO:")
    variaciones = [
        "+52 1 6624644200",
        "52 1 6624644200", 
        "5216624644200",
        "6624644200",
        "+521 6624644200",
        "521 6624644200"
    ]
    
    for variacion in variaciones:
        print(f"   🔍 Probando: {variacion}")
        resultado = buscar_usuario_por_telefono(variacion, nombre_nora)
        if resultado:
            print(f"      ✅ ENCONTRADO - {resultado.get('nombre', 'Sin nombre')}")
        else:
            print(f"      ❌ No encontrado")
    print()
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN DEL TEST:")
    print("=" * 60)
    
    if usuario_encontrado:
        print("✅ TU NÚMERO ESTÁ REGISTRADO EN EL SISTEMA")
        print(f"👤 Te identificas como: {usuario_encontrado.get('nombre', 'Sin nombre')}")
        print(f"🏷️ Con el rol: {usuario_encontrado.get('rol', 'Sin rol')}")
        
        if tipo_contacto.get('tipo') == 'usuario_cliente':
            print("🎯 Serás identificado como USUARIO INTERNO en WhatsApp")
            print("📱 Tendrás acceso a menús especiales y modo sin restricciones")
        elif tipo_contacto.get('tipo') == 'cliente':
            print("🎯 Serás identificado como CLIENTE en WhatsApp") 
            print("📱 Tendrás acceso a información de tu cuenta")
        else:
            print("🎯 Serás tratado como VISITANTE en WhatsApp")
            print("📱 Acceso limitado hasta registro")
            
    else:
        print("❌ TU NÚMERO NO ESTÁ REGISTRADO EN EL SISTEMA")
        print("📝 Necesitas ser agregado a la tabla usuarios_clientes")
        print("🎯 Actualmente serás tratado como VISITANTE en WhatsApp")
    
    print("=" * 60)

if __name__ == "__main__":
    test_mi_numero_celular()
