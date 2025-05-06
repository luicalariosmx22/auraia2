from supabase import create_client
from dotenv import load_dotenv
import os
from app import safe_register_blueprint  # Import the safe_register_blueprint utility

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
            from clientes.aura.routes.panel_cliente import panel_cliente_bp
            safe_register_blueprint(app, panel_cliente_bp, url_prefix=f"/panel_cliente/{nombre_nora}")

        # Contactos
        if "panel_cliente_contactos" in modulos:
            from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
            safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/contactos")

        # Envíos
        if "panel_cliente_envios" in modulos:
            from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
            safe_register_blueprint(app, panel_cliente_envios_bp, url_prefix=f"/panel_cliente/{nombre_nora}/envios")

        # IA
        if "panel_cliente_ia" in modulos:
            from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
            safe_register_blueprint(app, panel_cliente_ia_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ia")

        # Respuestas
        if "panel_cliente_respuestas" in modulos:
            from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
            safe_register_blueprint(app, panel_cliente_respuestas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/respuestas")

        # Etiquetas
        if "panel_cliente_etiquetas" in modulos:
            from clientes.aura.routes.etiquetas import etiquetas_bp
            safe_register_blueprint(app, etiquetas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/etiquetas")

        # Panel Chat
        if "panel_chat" in modulos:
            from clientes.aura.routes.panel_chat import panel_chat_bp
            safe_register_blueprint(app, panel_chat_bp, url_prefix=f"/panel_chat/{nombre_nora}")

        # Panel de conocimiento
        if "panel_conocimiento" in modulos:
            from clientes.aura.routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
            safe_register_blueprint(app, panel_cliente_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/conocimiento")

        # Ads
        if "ads" in modulos:
            from clientes.aura.routes.panel_cliente_ads import panel_cliente_ads_bp
            safe_register_blueprint(app, panel_cliente_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ads")

        print(f"✅ Todos los blueprints dinámicos para {nombre_nora} registrados correctamente.")

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos: {str(e)}")
