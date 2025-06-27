#!/usr/bin/env python3
"""
🎯 Test especial para la función de reconocimiento del admin Luica Larios
Prueba la respuesta personalizada cuando pregunta "¿Sabes quién soy?"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.handlers.handle_ai import detectar_pregunta_admin_especial, manejar_respuesta_ai
from clientes.aura.auth.google_login import buscar_usuario_por_telefono

def test_reconocimiento_admin():
    """Test de reconocimiento especial del admin"""
    print("=" * 70)
    print("🎯 TEST: RECONOCIMIENTO ESPECIAL DEL ADMIN LUICA LARIOS")
    print("=" * 70)
    
    # Tu número de teléfono
    telefono_admin = "+52 1 6624644200"
    nombre_nora = "aura"
    
    # 1. Obtener datos del usuario desde BD
    print(f"🔍 Paso 1: Buscando datos del admin...")
    usuario_admin = buscar_usuario_por_telefono(telefono_admin, nombre_nora)
    
    if not usuario_admin:
        print("❌ ERROR: No se encontró el usuario admin en la BD")
        return
    
    print(f"✅ Admin encontrado: {usuario_admin['nombre']}")
    print(f"📧 Email: {usuario_admin.get('correo')}")
    print(f"🏷️ Rol: {usuario_admin.get('rol')}")
    print()
    
    # 2. Crear objeto tipo_contacto
    tipo_contacto = {
        "tipo": "usuario_cliente",
        "nombre": usuario_admin["nombre"],
        "correo": usuario_admin.get("correo"),
        "telefono": usuario_admin.get("telefono"),
        "rol": usuario_admin.get("rol"),
        "es_supervisor": usuario_admin.get("es_supervisor", False),
        "modulos": usuario_admin.get("modulos", [])
    }
    
    # 3. Test de diferentes frases de reconocimiento
    frases_test = [
        "¿Sabes quién soy?",
        "Sabes quien soy",
        "¿Me conoces?",
        "¿Sabes quién es tu creador?",
        "Soy tu creador",
        "¿Quién soy yo?",
        "Hola, ¿me recuerdas?"
    ]
    
    print("🧪 Paso 2: Probando frases de reconocimiento...")
    print()
    
    for i, frase in enumerate(frases_test, 1):
        print(f"📝 Test {i}: '{frase}'")
        
        # Test con función directa
        respuesta_especial = detectar_pregunta_admin_especial(frase, tipo_contacto)
        
        if respuesta_especial:
            print("✅ RESPUESTA ESPECIAL ACTIVADA")
            print("🎯 Respuesta:")
            print("-" * 50)
            print(respuesta_especial)
            print("-" * 50)
            break
        else:
            print("⚠️ No se activó respuesta especial")
    
    print()
    
    # 4. Test completo con manejar_respuesta_ai
    print("🚀 Paso 3: Test completo con IA...")
    print()
    
    frase_principal = "¿Sabes quién soy?"
    respuesta, historial = manejar_respuesta_ai(
        mensaje_usuario=frase_principal,
        nombre_nora=nombre_nora,
        tipo_contacto=tipo_contacto
    )
    
    print(f"💬 Pregunta: {frase_principal}")
    print(f"🤖 Respuesta de Nora:")
    print("=" * 50)
    print(respuesta)
    print("=" * 50)
    print()
    
    # 5. Verificación de datos específicos
    print("🔍 Paso 4: Verificación de datos específicos...")
    if respuesta:
        verificaciones = [
            ("Nombre Luica Larios", "luica larios" in respuesta.lower()),
            ("Referencia a creador", "creador" in respuesta.lower()),
            ("Teléfono mencionado", telefono_admin.replace(" ", "")[-10:] in respuesta.replace(" ", "")),
            ("Rol SuperAdmin", "superadmin" in respuesta.lower()),
            ("Tono personalizado", "guapo" in respuesta.lower() or "inteligente" in respuesta.lower()),
            ("Emojis incluidos", "🌟" in respuesta or "👑" in respuesta or "🚀" in respuesta)
        ]
        
        for desc, resultado in verificaciones:
            status = "✅" if resultado else "❌"
            print(f"{status} {desc}: {'Correcto' if resultado else 'No encontrado'}")
    
    print()
    print("=" * 70)
    print("🎯 TEST COMPLETADO - RECONOCIMIENTO DEL ADMIN")
    print("=" * 70)

def test_usuario_normal():
    """Test para verificar que usuarios normales no activen la respuesta especial"""
    print()
    print("🧪 TEST ADICIONAL: Usuario normal (no debe activar respuesta especial)")
    print("-" * 50)
    
    # Simular usuario normal
    tipo_contacto_normal = {
        "tipo": "cliente",
        "nombre": "Juan Pérez",
        "correo": "juan@test.com",
        "telefono": "1234567890",
        "rol": "cliente",
        "es_supervisor": False
    }
    
    respuesta_especial = detectar_pregunta_admin_especial("¿Sabes quién soy?", tipo_contacto_normal)
    
    if respuesta_especial:
        print("❌ ERROR: Usuario normal activó respuesta especial")
    else:
        print("✅ CORRECTO: Usuario normal no activó respuesta especial")

if __name__ == "__main__":
    test_reconocimiento_admin()
    test_usuario_normal()
