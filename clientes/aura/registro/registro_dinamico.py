from supabase import create_client
from dotenv import load_dotenv
import os
import json

from clientes.aura.routes.panel_cliente import crear_blueprint_panel_cliente
from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
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
            modulos_raw = modulos_activados.data.get('modulos', [])
            if modulos_raw and isinstance(modulos_raw[0], dict):
                modulos = [m["nombre"].strip().lower().replace(" ", "_") for m in modulos_raw]
            else:
                modulos_raw = [{"nombre": m} for m in modulos_raw]
                modulos = [m["nombre"].strip().lower().replace(" ", "_") for m in modulos_raw]
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

            if "panel_conocimiento" in modulos:
                from clientes.aura.routes.panel_cliente_conocimiento import panel_cliente_conocimiento_bp
                safe_register_blueprint(app, panel_cliente_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/panel_conocimiento")

            if "panel_chat" in modulos:
                safe_register_blueprint(app, panel_chat_bp, url_prefix=f"/panel_cliente/{nombre_nora}/panel_chat")

            if "meta_ads" in modulos:
                # from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                # safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                pass  # Registro deshabilitado por error de import

            if "ads" in modulos:
                safe_register_blueprint(app, panel_cliente_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ads")

            if "contactos" in modulos:
                safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/contactos")

            if "envios" in modulos:
                safe_register_blueprint(app, panel_cliente_envios_bp, url_prefix=f"/panel_cliente/{nombre_nora}/envios")

            if "ia" in modulos:
                safe_register_blueprint(app, panel_cliente_ia_bp, url_prefix=f"/panel_cliente/{nombre_nora}/ia")

            if "respuestas" in modulos:
                safe_register_blueprint(app, panel_cliente_respuestas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/respuestas")

            if "clientes" in modulos:
                safe_register_blueprint(app, panel_cliente_clientes_bp, url_prefix=f"/panel_cliente/{nombre_nora}/clientes")

            if "qr_whatsapp_web" in modulos:
                safe_register_blueprint(app, panel_cliente_whatsapp_bp, url_prefix=f"/panel_cliente/{nombre_nora}/whatsapp")

            # Registrar módulo Meta Ads si está activo
            if "meta_ads" in modulos:
                # from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                # safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                pass  # Registro deshabilitado por error de import

            if "login" in modulos:
                safe_register_blueprint(app, login_bp, url_prefix=f"/login")

            # ✅ Diagnóstico detallado de módulos y rutas registradas

            modulos_url_esperada = {
                "pagos": f"/panel_cliente/{nombre_nora}/pagos",
                "tareas": f"/panel_cliente/{nombre_nora}/tareas",
                "etiquetas": f"/panel_cliente/{nombre_nora}/etiquetas",
                "panel_conocimiento": f"/panel_cliente/{nombre_nora}/panel_conocimiento",
                "panel_chat": f"/panel_cliente/{nombre_nora}/panel_chat",
                "meta_ads": f"/panel_cliente/{nombre_nora}/meta_ads",
                "ads": f"/panel_cliente/{nombre_nora}/ads",
                "qr_whatsapp_web": f"/panel_cliente/{nombre_nora}/whatsapp",
                "clientes": f"/panel_cliente/{nombre_nora}/clientes"
            }

            # Obtener rutas reales registradas
            rutas_registradas = [str(rule.rule) for rule in app.url_map.iter_rules()]

            print("\n🧪 Resultado del registro de módulos para:", nombre_nora)
            for modulo in modulos:
                ruta_esperada = modulos_url_esperada.get(modulo)
                if not ruta_esperada:
                    print(f"⚠️ {modulo.ljust(22)} → No definida en verificador")
                    continue

                if ruta_esperada in rutas_registradas:
                    print(f"✔ {modulo.ljust(22)} → Registrado ✅   ({ruta_esperada})")
                else:
                    print(f"❌ {modulo.ljust(22)} → NO registrado ⛔ ({ruta_esperada})")

        else:
            print(f"⚠️ No se encontraron módulos activados para {nombre_nora} en la tabla configuracion_bot.")

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos para {nombre_nora}: {e}")
