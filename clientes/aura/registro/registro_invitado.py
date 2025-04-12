def registrar_blueprints_invitado(app):
    try:
        # Ejemplo de una landing page pública o demo
        from clientes.aura.routes.landing import landing_bp
        app.register_blueprint(landing_bp)

        print("✅ Invitado blueprints registrados")
    except Exception as e:
        print("❌ Error en registrar_blueprints_invitado:", str(e))
