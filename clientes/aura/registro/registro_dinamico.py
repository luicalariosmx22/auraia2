from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_blueprints_por_nora(app, nombre_nora):
    try:
        print(f"🔍 Registrando blueprints dinámicos para la Nora: {nombre_nora}...")

        # Consultar módulos activos desde Supabase
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        modulos = response.data[0].get("modulos", []) if response.data else []

        print(f"📦 Módulos activos para {nombre_nora}: {modulos}")

        # Panel principal
        if "panel_cliente" in modulos:
            if "panel_cliente" not in app.blueprints:
                from clientes.aura.routes.panel_cliente import panel_cliente_bp
                app.register_blueprint(panel_cliente_bp, url_prefix="/panel_cliente")
                print("✅ Blueprint 'panel_cliente' registrado en /panel_cliente")
        
        # Contactos (ruta: /panel_cliente/contactos/<nombre_nora>)
        if "panel_cliente_contactos" in modulos:
            if "panel_cliente_contactos" not in app.blueprints:
                from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
                app.register_blueprint(panel_cliente_contactos_bp, url_prefix="/panel_cliente/contactos")
                print("✅ Blueprint 'panel_cliente_contactos' registrado en /panel_cliente/contactos")

        # Envíos (ruta: /panel_cliente/envios/<nombre_nora>)
        if "panel_cliente_envios" in modulos:
            if "panel_cliente_envios" not in app.blueprints:
                from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
                app.register_blueprint(panel_cliente_envios_bp, url_prefix="/panel_cliente/envios")
                print("✅ Blueprint 'panel_cliente_envios' registrado en /panel_cliente/envios")

        # IA (ruta: /panel_cliente/ia/<nombre_nora>)
        if "panel_cliente_ia" in modulos:
            if "panel_cliente_ia" not in app.blueprints:
                from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
                app.register_blueprint(panel_cliente_ia_bp, url_prefix="/panel_cliente/ia")
                print("✅ Blueprint 'panel_cliente_ia' registrado en /panel_cliente/ia")

        # Respuestas (ruta: /panel_cliente/respuestas/<nombre_nora>)
        if "panel_cliente_respuestas" in modulos:
            if "panel_cliente_respuestas" not in app.blueprints:
                from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
                app.register_blueprint(panel_cliente_respuestas_bp, url_prefix="/panel_cliente/respuestas")
                print("✅ Blueprint 'panel_cliente_respuestas' registrado en /panel_cliente/respuestas")

        # Etiquetas (ruta: /panel_cliente/etiquetas/<nombre_nora>)
        if "panel_cliente_etiquetas" in modulos:
            if "panel_cliente_etiquetas" not in app.blueprints:
                from clientes.aura.routes.etiquetas import etiquetas_bp
                app.register_blueprint(etiquetas_bp, url_prefix="/panel_cliente/etiquetas")
                print("✅ Blueprint 'panel_cliente_etiquetas' registrado en /panel_cliente/etiquetas")

        # Panel Chat (ruta: /panel_chat/<nombre_nora>)
        if "panel_chat" in modulos:
            if "panel_chat" not in app.blueprints:
                from clientes.aura.routes.panel_chat import panel_chat_bp
                app.register_blueprint(panel_chat_bp, url_prefix="/panel_chat")
                print("✅ Blueprint 'panel_chat' registrado en /panel_chat")

        # Panel de conocimiento (ruta: /panel_cliente/conocimiento/<nombre_nora>)
        if "panel_conocimiento" in modulos:
            if "panel_cliente_conocimiento" not in app.blueprints:
                from clientes.aura.routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
                app.register_blueprint(panel_cliente_conocimiento_bp, url_prefix="/panel_cliente/conocimiento")
                print("✅ Blueprint 'panel_cliente_conocimiento' registrado en /panel_cliente/conocimiento")

        # Ads (ruta: /panel_cliente/<nombre_nora>/ads)
        if "ads" in modulos:
            ruta_ads = f"/panel_cliente/{nombre_nora}/ads"
            if f"{nombre_nora}_ads" not in app.blueprints:
                from clientes.aura.modules.ads import ads_bp
                app.register_blueprint(ads_bp, url_prefix=ruta_ads)
                print(f"✅ Blueprint 'ads' registrado en {ruta_ads}")

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos: {str(e)}")
