print("✅ registro_admin.py cargado correctamente")

def registrar_blueprints_admin(app):
    try:
        print("🔍 Registrando blueprints de administración...")

        # 📋 Panel general con lista de Noras
        from clientes.aura.routes.admin_noras import admin_noras_bp
        app.register_blueprint(admin_noras_bp)  # /admin
        print("✅ Blueprint 'admin_noras_bp' registrado correctamente.")

        # 📊 Dashboard por Nora (IA, contactos, respuestas, tickets)
        from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
        app.register_blueprint(admin_nora_dashboard_bp)  # /admin/nora/<nombre_nora>/dashboard
        print("✅ Blueprint 'admin_nora_dashboard_bp' registrado correctamente.")

        # ✏️ Editor de configuración de cada Nora
        from clientes.aura.routes.admin_nora import admin_nora_bp
        app.register_blueprint(admin_nora_bp)  # /admin/nora/<nombre_nora>/editar
        print("✅ Blueprint 'admin_nora_bp' registrado correctamente.")

        # 📤 Módulo de envíos programados por etiqueta
        from clientes.aura.routes.envios_programados import envios_programados_bp
        app.register_blueprint(envios_programados_bp)  # /panel/envios-programados y /api/envios-programados
        print("✅ Blueprint 'envios_programados_bp' registrado correctamente.")

        print("✅ Todos los blueprints de administración registrados correctamente.")

    except Exception as e:
        print(f"❌ Error en registrar_blueprints_admin: {str(e)}")
