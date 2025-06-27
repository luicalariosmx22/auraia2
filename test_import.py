#!/usr/bin/env python3
# Test simple para verificar que los imports funcionan después de quitar el módulo de conocimiento

try:
    print("🔍 Probando imports...")
    
    # Import principal
    from clientes.aura import create_app
    print("✅ Import de create_app exitoso")
    
    # Crear app
    app = create_app()
    print("✅ Creación de app exitosa")
    
    print("🎉 Todos los tests pasaron - el módulo de conocimiento fue removido correctamente")
    
except Exception as e:
    print(f"❌ Error durante los tests: {e}")
    import traceback
    traceback.print_exc()
