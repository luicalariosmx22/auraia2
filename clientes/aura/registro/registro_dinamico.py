from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_blueprints_por_nora(app, nombre_nora):
    print(f"⚙️ Registrando módulos activos para Nora: {nombre_nora}")

    # Consultar módulos activos desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        if response.error or not response.data:
            print(f"❌ No se encontraron módulos para {nombre_nora} en Supabase")
            return

        modulos = response.data[0].get("modulos", [])
        print(f"🔍 Módulos encontrados en Supabase: {modulos}")
    except Exception as e:
        print(f"❌ Error al consultar módulos en Supabase: {str(e)}")
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