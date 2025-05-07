from supabase import create_client
from dotenv import load_dotenv
import os

from clientes.aura.routes.panel_cliente import panel_cliente_bp
from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
from clientes.aura.routes.etiquetas import etiquetas_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
from clientes.aura.routes.panel_cliente_ads import panel_cliente_ads_bp
from clientes.aura.routes.panel_cliente_clientes import panel_cliente_clientes_bp
from clientes.aura.utils.validar_modulo_activo import modulo_activo_para_nora

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_blueprints_por_nora(app, nombre_nora, safe_register_blueprint):
    from clientes.aura.modules.ads import ads_bp  # ✅ Import del módulo Ads dinámico

    print(f"🔍 Registrando blueprints dinámicos para {nombre_nora}...")

    try:
        # ✅ Este es el contenedor base del panel cliente, siempre se registra
        safe_register_blueprint(app, panel_cliente_bp, url_prefix=f"/panel_cliente/{nombre_nora}")

        if modulo_activo_para_nora(nombre_nora, "contactos"):
            safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/contactos")

        if modulo_activo_para_nora(nombre_nora, "envios"):
            safe_register_blueprint(app, panel_cliente_envios_bp, url_prefix=f"/panel_cliente/{nombre_nora}/envios")

        if modulo_activo_para_nora(nombre_nora, "ia"):
            safe_register_blueprint(app, panel_cliente_ia_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ia")

        if modulo_activo_para_nora(nombre_nora, "respuestas"):
            safe_register_blueprint(app, panel_cliente_respuestas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/respuestas")

        if modulo_activo_para_nora(nombre_nora, "etiquetas"):
            safe_register_blueprint(app, etiquetas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/etiquetas")

        if modulo_activo_para_nora(nombre_nora, "chat"):
            safe_register_blueprint(app, panel_chat_bp, url_prefix=f"/panel_cliente/{nombre_nora}/chat")

        if modulo_activo_para_nora(nombre_nora, "conocimiento"):
            safe_register_blueprint(app, panel_cliente_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/conocimiento")

        if modulo_activo_para_nora(nombre_nora, "clientes"):
            safe_register_blueprint(app, panel_cliente_clientes_bp, url_prefix=f"/panel_cliente/{nombre_nora}/clientes")

        # ✅ Registrar la ruta dinámica del módulo Ads si está activo
        if modulo_activo_para_nora(nombre_nora, "ads"):
            if f"{nombre_nora}_ads" not in app.blueprints:
                app.add_url_rule(
                    f"/panel_cliente/{nombre_nora}/ads",
                    view_func=ads_bp.view_functions['panel_ads'],  # Correct function name
                    endpoint=f"{nombre_nora}_ads"
                )
                print(f"✅ Blueprint 'ads' registrado para {nombre_nora}")
            else:
                print(f"⚠️ Blueprint 'ads' ya estaba registrado para {nombre_nora}")

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos para {nombre_nora}: {e}")
