import json
import os

def registrar_blueprints_por_nora(app, nombre_nora):
    print(f"⚙️ Registrando módulos activos para Nora: {nombre_nora}")

    config_path = f"clientes/{nombre_nora}/config.json"
    if not os.path.exists(config_path):
        print(f"❌ No existe config.json para {nombre_nora}")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        modulos = config.get("modulos", [])
    except Exception as e:
        print(f"❌ Error al leer config.json: {str(e)}")
        return

    try:
        if "contactos" in modulos:
            from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
            app.register_blueprint(panel_cliente_contactos_bp)
            print("✅ Módulo: contactos")

        if "ia" in modulos:
            from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
            app.register_blueprint(panel_cliente_ia_bp)
            print("✅ Módulo: ia")

        if "respuestas" in modulos:
            from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
            app.register_blueprint(panel_cliente_respuestas_bp)
            print("✅ Módulo: respuestas")

        # Aquí puedes seguir agregando nuevos módulos como "crm", "envios", "soporte", etc.
    except Exception as e:
        print(f"❌ Error al registrar módulos dinámicos: {str(e)}")
