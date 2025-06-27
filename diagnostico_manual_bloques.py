#!/usr/bin/env python3
"""
Script para diagnosticar el problema específico de los bloques post-login
"""

def test_manual_login():
    """Test manual usando curl para verificar el problema"""
    
    print("🔍 Diagnóstico Manual de Login y Bloques")
    print("=" * 50)
    
    print("\n1. 📋 Para probar manualmente, abre tu navegador en:")
    print("   http://localhost:5000/login/simple")
    
    print("\n2. 🔐 Usa estas credenciales:")
    print("   Email: admin@test.com")
    print("   Password: 123456")
    
    print("\n3. 🎯 Después del login, ve a:")
    print("   http://localhost:5000/panel_cliente/aura/entrenar")
    
    print("\n4. 🔧 Abre DevTools (F12) y ve a la pestaña Console")
    print("   Busca mensajes que empiecen con '🔄 Cargando conocimiento desde:'")
    
    print("\n5. 📦 También ve a la pestaña Network y busca:")
    print("   GET /panel_cliente/aura/entrenar/bloques")
    print("   - Si el status es 200: El endpoint funciona")
    print("   - Si el status es 302: Problema de sesión (redirigido a login)")
    print("   - Si el status es 500: Error del servidor")
    
    print("\n6. 🧪 Para probar directamente el endpoint, después del login ejecuta en la consola:")
    print("   fetch('/panel_cliente/aura/entrenar/bloques').then(r => r.json()).then(console.log)")
    
    print("\n" + "=" * 50)
    
    # También vamos a crear un endpoint temporal para debug
    print("\n🔧 Creando endpoint temporal de debug...")

def crear_endpoint_debug():
    """Crear un endpoint temporal para debug de sesión"""
    
    debug_code = '''
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/debug/session", methods=["GET"])
def debug_session(nombre_nora):
    """Endpoint temporal para debug de sesión"""
    from flask import session, jsonify
    
    return jsonify({
        "session_keys": list(session.keys()),
        "session_data": dict(session),
        "has_email": bool(session.get("email")),
        "has_nombre_nora": bool(session.get("nombre_nora")),
        "nombre_nora_value": session.get("nombre_nora"),
        "is_authenticated": bool(session.get("email") and session.get("nombre_nora")),
        "requested_nora": nombre_nora
    })
'''
    
    print("📝 Código para agregar al final de cliente_nora.py:")
    print(debug_code)
    
    return debug_code

if __name__ == "__main__":
    test_manual_login()
    debug_code = crear_endpoint_debug()
    
    # Vamos a agregar el endpoint de debug al archivo
    import os
    
    archivo_cliente = os.path.join(os.path.dirname(__file__), "clientes", "aura", "routes", "cliente_nora.py")
    
    try:
        with open(archivo_cliente, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if "debug/session" not in contenido:
            print(f"\n✅ Agregando endpoint de debug a {archivo_cliente}")
            
            # Agregar al final del archivo, antes del último comentario o línea
            nuevo_contenido = contenido.rstrip() + "\n\n" + debug_code.strip() + "\n"
            
            with open(archivo_cliente, 'w', encoding='utf-8') as f:
                f.write(nuevo_contenido)
            
            print("✅ Endpoint de debug agregado")
            print("🔄 Reinicia el servidor y luego ve a:")
            print("   http://localhost:5000/panel_cliente/aura/debug/session")
        else:
            print("ℹ️ Endpoint de debug ya existe")
    
    except Exception as e:
        print(f"❌ Error agregando endpoint de debug: {e}")
        print("📝 Agrega manualmente el código mostrado arriba")
