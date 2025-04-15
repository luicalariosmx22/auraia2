print("✅ registro_cliente.py cargado correctamente")

def registrar_blueprints_cliente(app):
    try:
        # Panel general
        from clientes.aura.routes.panel_cliente import panel_cliente_bp
        app.register_blueprint(panel_cliente_bp)

        # Módulos separados
        from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
        from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
        from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp

        app.register_blueprint(panel_cliente_contactos_bp)
        app.register_blueprint(panel_cliente_ia_bp)
        app.register_blueprint(panel_cliente_respuestas_bp)
        app.register_blueprint(panel_cliente_envios_bp)

        print("✅ Blueprints cliente registrados")

    except Exception as e:
        print("❌ Error en registrar_blueprints_cliente:", str(e))
