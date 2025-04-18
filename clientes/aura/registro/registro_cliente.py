print("✅ registro_cliente.py cargado correctamente")

def registrar_blueprints_cliente(app):
    try:
        print("🔍 Registrando blueprints del cliente...")

        # 📋 Panel general
        from clientes.aura.routes.panel_cliente import panel_cliente_bp
        if "panel_cliente" not in app.blueprints:
            app.register_blueprint(panel_cliente_bp)
            print("✅ Blueprint 'panel_cliente_bp' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'panel_cliente_bp' ya estaba registrado.")

        # 📂 Módulos separados
        from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
        from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
        from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
        from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp

        if "panel_cliente_contactos" not in app.blueprints:
            app.register_blueprint(panel_cliente_contactos_bp)
            print("✅ Blueprint 'panel_cliente_contactos_bp' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'panel_cliente_contactos_bp' ya estaba registrado.")

        if "panel_cliente_ia" not in app.blueprints:
            app.register_blueprint(panel_cliente_ia_bp)
            print("✅ Blueprint 'panel_cliente_ia_bp' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'panel_cliente_ia_bp' ya estaba registrado.")

        if "panel_cliente_respuestas" not in app.blueprints:
            app.register_blueprint(panel_cliente_respuestas_bp)
            print("✅ Blueprint 'panel_cliente_respuestas_bp' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'panel_cliente_respuestas_bp' ya estaba registrado.")

        if "panel_cliente_envios" not in app.blueprints:
            app.register_blueprint(panel_cliente_envios_bp)
            print("✅ Blueprint 'panel_cliente_envios_bp' registrado correctamente.")
        else:
            print("⚠️ Blueprint 'panel_cliente_envios_bp' ya estaba registrado.")

        print("✅ Todos los blueprints del cliente registrados correctamente.")

    except Exception as e:
        print(f"❌ Error en registrar_blueprints_cliente: {str(e)}")
