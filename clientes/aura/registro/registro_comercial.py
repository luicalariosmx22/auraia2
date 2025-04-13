def registrar_blueprints_comercial(app):
    try:
        # Ejemplo: módulo de campañas o reportes
        from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
        app.register_blueprint(panel_cliente_envios_bp)

        print("✅ Comercial blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_comercial:", str(e))
