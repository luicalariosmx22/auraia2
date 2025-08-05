"""
Script para diagnosticar y corregir problemas de rutas en AuraAi2.
"""
import os
import logging
from dotenv import load_dotenv

# Configurar logging básico
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Función principal para diagnosticar y corregir rutas de la aplicación.
    """
    # Cargar variables de entorno necesarias
    load_dotenv(".env.local")
    
    # Importar app de forma segura
    try:
        from gunicorn_patch import app, socketio
        
        # Normalizar la instancia de la app
        if isinstance(app, tuple) and len(app) >= 1:
            app_instance = app[0]
        else:
            app_instance = app
            
        # Mostrar todas las rutas registradas para diagnóstico
        print("\n📋 LISTADO DE RUTAS REGISTRADAS:")
        routes = []
        for rule in sorted(app_instance.url_map.iter_rules(), key=lambda x: str(x)):
            routes.append((str(rule), rule.endpoint))
            print(f"  • {rule.endpoint:<40} -> {rule}")
            
        # Buscar específicamente rutas de login
        print("\n🔍 BÚSQUEDA DE RUTAS DE LOGIN:")
        login_routes = [r for r in routes if 'login' in r[0].lower() or 'login' in r[1].lower()]
        if login_routes:
            for route, endpoint in login_routes:
                print(f"  ✓ {endpoint:<40} -> {route}")
        else:
            print("  ❌ No se encontraron rutas relacionadas con login")
            
        # Verificar blueprint de simple_login
        print("\n🔧 VERIFICANDO BLUEPRINT DE LOGIN SIMPLE:")
        verificar_y_corregir_login_simple(app_instance)
        
    except Exception as e:
        logger.error(f"Error al diagnosticar rutas: {str(e)}", exc_info=True)
        print(f"❌ Error: {str(e)}")

def verificar_y_corregir_login_simple(app):
    """
    Verifica y corrige el blueprint de login simple.
    
    Args:
        app: La instancia de la aplicación Flask
    """
    try:
        # Verificar si el blueprint ya está registrado
        blueprint_registrado = False
        for blueprint in getattr(app, 'blueprints', {}).values():
            if 'login' in blueprint.name.lower() and hasattr(blueprint, 'url_prefix'):
                print(f"  • Blueprint encontrado: {blueprint.name} con prefijo {blueprint.url_prefix}")
                blueprint_registrado = True
        
        if not blueprint_registrado:
            print("  ❌ No se encontraron blueprints de login registrados")
            
            # Intentar registrar el blueprint
            try:
                # Importar función de registro de login
                from clientes.aura.registro.registro_login import registrar_blueprints_login
                from clientes.aura import safe_register_blueprint
                
                print("  🔄 Intentando registrar blueprints de login...")
                registrar_blueprints_login(app, safe_register_blueprint)
                print("  ✅ Blueprints de login registrados correctamente")
                
                # Mostrar las rutas nuevamente
                print("\n📋 RUTAS ACTUALIZADAS:")
                for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
                    if 'login' in str(rule).lower() or 'login' in rule.endpoint.lower():
                        print(f"  • {rule.endpoint:<40} -> {rule}")
            except Exception as e:
                print(f"  ❌ Error al registrar blueprints de login: {str(e)}")
                
                # Plan B: Registrar ruta de login simple directamente
                try:
                    print("  🔄 Intentando crear ruta de login básica...")
                    
                    @app.route('/login/simple', methods=['GET', 'POST'])
                    def login_simple():
                        return """
                        <html>
                            <head><title>Login Simple</title></head>
                            <body>
                                <h1>Login Simple de Emergencia</h1>
                                <form method="post">
                                    <div>Usuario: <input type="text" name="username"></div>
                                    <div>Contraseña: <input type="password" name="password"></div>
                                    <div><button type="submit">Ingresar</button></div>
                                </form>
                            </body>
                        </html>
                        """
                    
                    print("  ✅ Ruta de login básica creada en /login/simple")
                except Exception as login_error:
                    print(f"  ❌ No se pudo crear ruta de login básica: {str(login_error)}")
    except Exception as e:
        print(f"  ❌ Error general: {str(e)}")

if __name__ == "__main__":
    print("🔍 Iniciando diagnóstico de rutas de AuraAi2...")
    main()
    print("\n✅ Diagnóstico finalizado")