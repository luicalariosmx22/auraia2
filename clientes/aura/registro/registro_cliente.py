def registrar_blueprints_cliente(app):
    try:
        from clientes.aura.routes.panel_cliente import panel_cliente_bp
        from clientes.aura.routes.panel_chat import panel_chat_bp
        from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
        from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
        from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp

        app.register_blueprint(panel_cliente_bp)
        app.register_blueprint(panel_chat_bp)
        app.register_blueprint(panel_cliente_contactos_bp)
        app.register_blueprint(panel_cliente_ia_bp)
        app.register_blueprint(panel_cliente_respuestas_bp)

        print("✅ Cliente blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_cliente:", str(e))
