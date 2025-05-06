print("✅ registro_admin.py cargado correctamente")

from app import safe_register_blueprint  # Import the safe_register_blueprint utility

def registrar_blueprints_admin(app):
    try:
        print("🔍 Registrando blueprints de administración...")

        # 📋 Panel general con lista de Noras
        from clientes.aura.routes.admin_noras import admin_noras_bp
        safe_register_blueprint(app, admin_noras_bp, url_prefix="/admin/noras")

        # 📊 Dashboard por Nora (IA, contactos, respuestas, tickets)
        from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
        safe_register_blueprint(app, admin_nora_dashboard_bp, url_prefix="/admin/nora/<nombre_nora>/dashboard")

        # ✏️ Editor de configuración de cada Nora
        from clientes.aura.routes.admin_nora import admin_nora_bp
        safe_register_blueprint(app, admin_nora_bp, url_prefix="/admin/nora/<nombre_nora>/editar")

        # 📤 Módulo de envíos programados por etiqueta
        from clientes.aura.routes.envios_programados import envios_programados_bp
        safe_register_blueprint(app, envios_programados_bp, url_prefix="/panel/envios-programados")

        print("✅ Todos los blueprints de administración registrados correctamente.")

    except Exception as e:
        print(f"❌ Error en registrar_blueprints_admin: {str(e)}")
