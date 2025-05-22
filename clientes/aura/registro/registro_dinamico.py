from supabase import create_client
from dotenv import load_dotenv
import os
import json

from clientes.aura.routes.panel_cliente import crear_blueprint_panel_cliente
from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
from clientes.aura.routes.etiquetas import etiquetas_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
from clientes.aura.routes.panel_cliente_clientes import panel_cliente_clientes_bp
from clientes.aura.routes.panel_cliente_whatsapp.panel_cliente_whatsapp import panel_cliente_whatsapp_bp
from clientes.aura.routes.panel_cliente_ads import panel_cliente_ads_bp
from clientes.aura.routes.panel_cliente_tareas import panel_cliente_tareas_bp


# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def safe_register_blueprint(app, blueprint, **kwargs):
    if blueprint.name not in app.blueprints:
        app.register_blueprint(blueprint, **kwargs)
        print(f"✅ Blueprint '{blueprint.name}' registrado con prefijo '{kwargs.get('url_prefix', '')}'")
    else:
        print(f"⚠️ Blueprint '{blueprint.name}' ya estaba registrado.")

def registrar_blueprints_por_nora(app, nombre_nora, safe_register_blueprint):
    from clientes.aura.modules.ads import ads_bp  # ✅ Import del módulo Ads dinámico

    print(f"🔍 Registrando blueprints dinámicos para {nombre_nora}...")

    try:
        # 🧪 Debug print statement
        print(f"🧪 Registrando panel_cliente para {nombre_nora}")
        # Crear y registrar el blueprint dinámico del panel cliente
        bp = crear_blueprint_panel_cliente(nombre_nora)
        safe_register_blueprint(app, bp, url_prefix=f"/panel_cliente/{nombre_nora}")

        # 👉 Registra el módulo 'entrenamiento' para cada Nora
        from clientes.aura.routes.panel_cliente_entrenamiento.vista_panel_cliente_entrenamiento import panel_cliente_entrenamiento_bp
        safe_register_blueprint(app, panel_cliente_entrenamiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/entrenamiento")

        # Obtener los módulos activos de la tabla configuracion_bot
        modulos_activados = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', nombre_nora).single().execute()

        if modulos_activados.data:
            modulos_data = modulos_activados.data.get('modulos', [])
            
            # 🔧 Normalizar los nombres (ej. "Pagos" → "pagos", "Panel chat" → "panel_chat")
            modulos = [m["nombre"].strip().lower().replace(" ", "_") for m in modulos_data]
            
            print(f"🧪 Módulos activos normalizados para {nombre_nora}: {modulos}")

            # Ejemplo de comparaciones que ahora sí funcionarán:
            if "pagos" in modulos:
                from clientes.aura.routes.panel_cliente_pagos import (
                    panel_cliente_pagos_bp,
                    panel_cliente_pagos_servicios_bp,
                    panel_cliente_pagos_nuevo_bp,
                    panel_cliente_pagos_recibo_bp
                )
                safe_register_blueprint(app, panel_cliente_pagos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/pagos")
                safe_register_blueprint(app, panel_cliente_pagos_servicios_bp, url_prefix=f"/panel_cliente/{nombre_nora}/pagos/servicios")
                safe_register_blueprint(app, panel_cliente_pagos_nuevo_bp, url_prefix=f"/panel_cliente/{nombre_nora}/pagos")
                safe_register_blueprint(app, panel_cliente_pagos_recibo_bp)

            if "tareas" in modulos:
                from clientes.aura.routes.panel_cliente_tareas import panel_cliente_tareas_bp
                safe_register_blueprint(app, panel_cliente_tareas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/tareas")

            if "etiquetas" in modulos:
                safe_register_blueprint(app, etiquetas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/etiquetas")

            if "panel_conocimiento" in modulos:
                safe_register_blueprint(app, panel_cliente_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/panel_conocimiento")

            if "panel_chat" in modulos:
                safe_register_blueprint(app, panel_chat_bp, url_prefix=f"/panel_cliente/{nombre_nora}/panel_chat")

            if "meta_ads" in modulos:
                from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")

            if "ads" in modulos:
                safe_register_blueprint(app, panel_cliente_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ads")

            # Registrar módulo Meta Ads si está activo
            if "meta_ads" in modulos:
                from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")

            if "login" in modulos:
                safe_register_blueprint(app, login_bp, url_prefix=f"/login")

            # 🔍 Diagnóstico de módulos no registrados
            modulos_registrados = [
                "pagos", "tareas", "etiquetas", "panel_conocimiento", "panel_chat", 
                "meta_ads", "ads", "login"
            ]

            no_registrados = [m for m in modulos if m not in modulos_registrados]

            if no_registrados:
                print(f"⚠️ Algunos módulos están activos en Supabase pero no tienen blueprint registrado: {no_registrados}")
            else:
                print("✅ Todos los módulos activos tienen blueprint registrado.")

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos para {nombre_nora}: {e}")
