from clientes.aura.routes.debug_verificar import debug_verificar_bp

def registrar_blueprints_debug(app, safe_register_blueprint):
    try:
        safe_register_blueprint(app, debug_verificar_bp)
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_debug: {e}")
