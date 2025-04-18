import json
import os

def registrar_blueprints_por_nora(app, nombre_nora):
    print(f"⚙️ Registrando módulos activos para Nora: {nombre_nora}")

    # Ruta del archivo config.json
    config_path = f"clientes/{nombre_nora}/config.json"
    if not os.path.exists(config_path):
        print(f"❌ No existe config.json para {nombre_nora}")
        return

    # Leer el archivo config.json
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        modulos = config.get("modulos", [])
        print(f"🔍 Módulos encontrados en config.json: {modulos}")
    except Exception as e:
        print(f"❌ Error al leer config.json: {str(e)}")
        return

    # Registrar blueprints dinámicamente
    try:
        if "contactos" in modulos:
            from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
            app.register_blueprint(panel_cliente_contactos_bp)
            print("✅ Módulo: contactos registrado")

        if "ia" in modulos:
            try:
                from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
                app.register_blueprint(panel_cliente_ia_bp)
                print("✅ Módulo: ia registrado")
            except Exception as e:
                print(f"❌ Error al registrar el módulo IA: {str(e)}")

        if "respuestas" in modulos:
            from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
            app.register_blueprint(panel_cliente_respuestas_bp)
            print("✅ Módulo: respuestas registrado")

        if "envios" in modulos:
            from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
            app.register_blueprint(panel_cliente_envios_bp)
            print("✅ Módulo: envios programados registrado")

        if "qr_whatsapp_web" in modulos:
            print("🕐 Módulo QR WhatsApp Web (aún no implementado)")

        if "multi_nora" in modulos:
            print("🕐 Módulo multi_nora (aún no implementado)")

        if "pagos" in modulos:
            print("🕐 Módulo pagos (MercadoPago/PayPal) aún no implementado")

        if "redes_sociales" in modulos:
            print("🕐 Módulo integración Facebook/Instagram (futuro)")

        if "diseño_personalizado" in modulos:
            print("🕐 Módulo de personalización visual (futuro)")

        if "open_table" in modulos:
            print("🕐 Módulo integración con OpenTable (futuro)")

        if "google_calendar" in modulos:
            print("🕐 Módulo integración con Google Calendar (futuro)")

    except Exception as e:
        print(f"❌ Error al registrar módulos dinámicos: {str(e)}")
