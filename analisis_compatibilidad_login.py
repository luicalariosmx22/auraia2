#!/usr/bin/env python3
"""
Análisis de compatibilidad entre login simple y decorador login_required_cliente
"""

def analizar_compatibilidad():
    print("🔍 Análisis de Compatibilidad Login - Decorador")
    print("=" * 60)
    
    print("\n📋 KEYS QUE ESTABLECE EL LOGIN SIMPLE:")
    login_keys = [
        'session["email"] = email',
        'session["name"] = usuario["nombre"]', 
        'session["nombre_nora"] = usuario["nombre_nora"]',
        'session["is_admin"] = usuario["is_admin"]',
        'session["user"] = {...}'
    ]
    
    for key in login_keys:
        print(f"  ✅ {key}")
    
    print("\n🔒 KEYS QUE VERIFICA EL DECORADOR login_required_cliente:")
    decorador_checks = [
        'session.get("email")',
        'session.get("nombre_nora")'
    ]
    
    for check in decorador_checks:
        print(f"  🔍 {check}")
    
    print("\n✅ COMPATIBILIDAD:")
    print("  ✅ email: ✓ (establecido y verificado)")
    print("  ✅ nombre_nora: ✓ (establecido y verificado)")
    
    print("\n🤔 POSIBLE PROBLEMA:")
    print("  Las keys parecen compatibles, así que el problema podría ser:")
    print("  1. 🍪 Problemas con cookies/sesión de Flask")
    print("  2. 🔄 Timing - la sesión no se persiste entre requests")
    print("  3. 🚫 Configuración de Flask session")
    print("  4. 🌐 Diferente dominio/puerto entre login y endpoint")
    
    print("\n🔧 SOLUCIONES A PROBAR:")
    print("  1. Verificar configuración de SECRET_KEY en Flask")
    print("  2. Agregar logging al decorador para ver qué recibe")
    print("  3. Verificar que las cookies se establecen correctamente")
    print("  4. Probar con un decorador más permisivo temporalmente")

def crear_decorador_debug():
    """Crear una versión de debug del decorador"""
    
    decorador_debug = '''
def login_required_cliente_debug(f):
    """Versión debug del decorador para investigar problemas de sesión"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🔍 DEBUG - Verificando sesión para: {f.__name__}")
        print(f"📊 Session keys: {list(session.keys())}")
        print(f"📧 Email: {session.get('email', 'NO ENCONTRADO')}")
        print(f"🎯 Nombre Nora: {session.get('nombre_nora', 'NO ENCONTRADO')}")
        print(f"👤 User: {session.get('user', 'NO ENCONTRADO')}")
        print(f"🔑 Is Admin: {session.get('is_admin', 'NO ENCONTRADO')}")
        
        email_ok = bool(session.get("email"))
        nora_ok = bool(session.get("nombre_nora"))
        
        print(f"✅ Email OK: {email_ok}")
        print(f"✅ Nora OK: {nora_ok}")
        
        if not email_ok or not nora_ok:
            print(f"❌ Sesión inválida, redirigiendo a login")
            return redirect("/login/simple")
        
        print(f"✅ Sesión válida, continuando...")
        return f(*args, **kwargs)
    return decorated_function
'''
    
    print("\n📝 DECORADOR DE DEBUG para agregar a login_required.py:")
    print(decorador_debug)
    
    return decorador_debug

if __name__ == "__main__":
    analizar_compatibilidad()
    decorador_debug = crear_decorador_debug()
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Agregar el decorador de debug a login_required.py")
    print("2. Cambiar temporalmente el decorador en cliente_nora.py")
    print("3. Reiniciar servidor y probar")
    print("4. Revisar logs en consola del servidor")
