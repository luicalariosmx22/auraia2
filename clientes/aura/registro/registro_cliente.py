print("✅ registro_cliente.py cargado correctamente")

def registrar_blueprints_cliente(app):
    try:
        # Panel general
        from clientes.aura.routes.panel_cliente import panel_cliente_bp
        if "panel_cliente" not in app.blueprints:
            app.register_blueprint(panel_cliente_bp)

        # Módulos separados
        from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
        from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
        from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
        from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp

        if "panel_cliente_contactos" not in app.blueprints:
            app.register_blueprint(panel_cliente_contactos_bp)

        if "panel_cliente_ia" not in app.blueprints:
            app.register_blueprint(panel_cliente_ia_bp)

        if "panel_cliente_respuestas" not in app.blueprints:
            app.register_blueprint(panel_cliente_respuestas_bp)

        if "panel_cliente_envios" not in app.blueprints:
            app.register_blueprint(panel_cliente_envios_bp)

        print("✅ Blueprints cliente registrados")

    except Exception as e:
        print("❌ Error en registrar_blueprints_cliente:", str(e))
