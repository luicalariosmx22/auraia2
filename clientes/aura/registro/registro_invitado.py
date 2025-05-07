def registrar_blueprints_invitado(app, safe_register_blueprint):  # 🛠 Added safe_register_blueprint as an argument
    try:
        print("✅ Invitado blueprints registrados (no hay rutas por ahora)")
    except Exception as e:
        print("❌ Error en registrar_blueprints_invitado:", str(e))
