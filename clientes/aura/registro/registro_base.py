print("✅ registro_base.py cargado correctamente")

from clientes.aura.routes.webhook import webhook_bp

def registrar_blueprints_base(app, safe_register_blueprint):
    """
    ✅ Registra rutas base globales (no ligadas a administración).
    """
    try:
        safe_register_blueprint(app, webhook_bp)
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_base: {e}")
