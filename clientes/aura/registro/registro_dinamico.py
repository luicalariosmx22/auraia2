from supabase import create_client
from dotenv import load_dotenv
import os
import json

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
from utils.validar_modulo_activo import modulo_activo_para_nora

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

        # Obtener los módulos activos de la tabla configuracion_bot
        modulos_activados = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', nombre_nora).single().execute()

        # Verificar si se encontraron los datos
        if modulos_activados.data:
            modulos_data = modulos_activados.data['modulos']
            
            # Si los datos están en formato string JSON, conviértelos a lista
            if isinstance(modulos_data, str):
                modulos = json.loads(modulos_data)
            else:
                # Si ya es una lista, asignamos directamente
                modulos = modulos_data

            # Registrar blueprints según los módulos activos
            if "contactos" in modulos:
                safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/contactos")

            if "etiquetas" in modulos:
                safe_register_blueprint(app, etiquetas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/etiquetas")

            if "envios" in modulos:
                safe_register_blueprint(app, panel_cliente_envios_bp, url_prefix=f"/panel_cliente/{nombre_nora}/envios")

            if "ia" in modulos:
                safe_register_blueprint(app, panel_cliente_ia_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ia")

            if "respuestas" in modulos:
                safe_register_blueprint(app, panel_cliente_respuestas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/respuestas")

            if "chat" in modulos:
                safe_register_blueprint(app, panel_chat_bp, url_prefix=f"/panel_cliente/{nombre_nora}/chat")

            if "conocimiento" in modulos:
                safe_register_blueprint(app, panel_cliente_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/conocimiento")

            if "clientes" in modulos:
                safe_register_blueprint(app, panel_cliente_clientes_bp, url_prefix=f"/panel_cliente/{nombre_nora}/clientes")

            if "ads" in modulos:
                if f"{nombre_nora}_ads" not in app.blueprints:
                    app.add_url_rule(
                        f"/panel_cliente/{nombre_nora}/ads",
                        view_func=panel_cliente_ads_bp.view_functions['panel_cliente_ads'],
                        endpoint=f"{nombre_nora}_ads"
                    )
                    print(f"✅ Blueprint 'ads' registrado para {nombre_nora}")
                else:
                    print(f"⚠️ Blueprint 'ads' ya estaba registrado para {nombre_nora}")

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos para {nombre_nora}: {e}")
