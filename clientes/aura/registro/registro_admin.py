print("✅ registro_admin.py cargado correctamente")

def registrar_blueprints_admin(app):
    try:
        # 📋 Panel general con lista de Noras
        from clientes.aura.routes.admin_noras import admin_noras_bp
        app.register_blueprint(admin_noras_bp)  # /admin

        # 📊 Dashboard por Nora (IA, contactos, respuestas, tickets)
        from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
        app.register_blueprint(admin_nora_dashboard_bp)  # /admin/nora/<nombre_nora>/dashboard

        # 🛠️ Futuro: edición directa de cada Nora
        # from clientes.aura.routes.admin_nora import admin_nora_bp
        # app.register_blueprint(admin_nora_bp)

        print("✅ Admin blueprints registrados")

    except Exception as e:
        print("❌ Error en registrar_blueprints_admin:", str(e))
