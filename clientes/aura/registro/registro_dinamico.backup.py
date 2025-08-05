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
from clientes.aura.routes.panel_cliente_clientes import panel_cliente_clientes_bp
from clientes.aura.routes.panel_cliente_ads import panel_cliente_ads_bp
from clientes.aura.routes.panel_cliente_tareas import panel_cliente_tareas_bp
from clientes.aura.routes.panel_cliente_cursos import panel_cliente_cursos_bp
from clientes.aura.routes.panel_cliente_whatsapp_web import panel_cliente_whatsapp_web_bp

from clientes.aura.routes.webhook_contactos import webhook_contactos_bp
from clientes.aura.routes.panel_team.vista_panel_team import panel_team_bp
from clientes.aura.routes.panel_cliente_tareas.recurrentes import panel_tareas_recurrentes_bp
from clientes.aura.routes.reportes_meta_ads import reportes_meta_ads_bp
from clientes.aura.routes.reportes_meta_ads import get_estadisticas_bp
from clientes.aura.routes.panel_cliente_google_ads import panel_cliente_google_ads_bp
from clientes.aura.routes.whatsapp_integration import whatsapp_integration_bp


# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_modulos_activos(nombre_nora):
    """
    Obtener los módulos activos para una Nora específica desde la base de datos.
    
    Args:
        nombre_nora (str): Nombre de la Nora para obtener los módulos
        
    Returns:
        list: Lista de módulos activos normalizados
    """
    try:
        # Obtener los módulos activos de la tabla configuracion_bot
        modulos_activados = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', nombre_nora).single().execute()

        if modulos_activados.data:
            modulos_raw = modulos_activados.data.get('modulos', [])
            if modulos_raw and isinstance(modulos_raw[0], dict):
                modulos = [
                    m["nombre"]
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("panel_conocimiento", "conocimiento")
                    .replace("panel_chat", "chat")
                    for m in modulos_raw
                ]
            else:
                modulos_raw = [{"nombre": m} for m in modulos_raw]
                modulos = [
                    m["nombre"]
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("panel_conocimiento", "conocimiento")
                    .replace("panel_chat", "chat")
                    for m in modulos_raw
                ]
            print(f"🧪 Módulos activos obtenidos para {nombre_nora}: {modulos}")
            return modulos
        else:
            print(f"⚠️ No se encontraron módulos activados para {nombre_nora} en la tabla configuracion_bot.")
            return []

    except Exception as e:
        print(f"❌ Error al obtener módulos activos para {nombre_nora}: {e}")
        return []

def safe_register_blueprint(app, blueprint, **kwargs):
    if blueprint.name not in app.blueprints:
        app.register_blueprint(blueprint, **kwargs)
        print(f"✅ Blueprint '{blueprint.name}' registrado con prefijo '{kwargs.get('url_prefix', '')}'")
    else:
        print(f"⚠️ Blueprint '{blueprint.name}' ya estaba registrado.")

def registrar_blueprints_por_nora(app, nombre_nora, safe_register_blueprint):
    # Obtener configuración de módulos
    try:
        config = supabase.table("configuracion_bot") \
            .select("modulos") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        modulos_activados = config.data.get("modulos", [])

    except Exception as e:
        print(f"❌ Error al obtener configuración de módulos para {nombre_nora}: {e}")
        modulos_activados = []

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

        # Otros módulos...
        if "contactos" in modulos_activados:
            # registrar_blueprint de contactos
            safe_register_blueprint(app, panel_cliente_contactos_bp, url_prefix=f"/panel_cliente/{nombre_nora}/contactos")

        # Registrar webhook para mensajes desde Node.js
        safe_register_blueprint(app, webhook_contactos_bp, url_prefix="/")

        # Obtener los módulos activos de la tabla configuracion_bot
        modulos_activados = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', nombre_nora).single().execute()

        if modulos_activados.data:
            modulos_raw = modulos_activados.data.get('modulos', [])
            if modulos_raw and isinstance(modulos_raw[0], dict):
                modulos = [
                    m["nombre"]
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("panel_conocimiento", "conocimiento")
                    .replace("panel_chat", "chat")
                    for m in modulos_raw
                ]
            else:
                modulos_raw = [{"nombre": m} for m in modulos_raw]
                modulos = [
                    m["nombre"]
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("panel_conocimiento", "conocimiento")
                    .replace("panel_chat", "chat")
                    for m in modulos_raw
                ]
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
                from clientes.aura.routes.panel_cliente_tareas import (
                    panel_cliente_tareas_bp
                )
                from clientes.aura.routes.panel_cliente_tareas.gestionar import panel_tareas_gestionar_bp
                from clientes.aura.routes.panel_cliente_tareas.tareas_crud import panel_tareas_crud_bp  # ✅ Agrega esta línea

                safe_register_blueprint(app, panel_cliente_tareas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/tareas")
                safe_register_blueprint(app, panel_tareas_gestionar_bp)
                safe_register_blueprint(app, panel_tareas_recurrentes_bp)
                safe_register_blueprint(app, panel_tareas_crud_bp)  # ✅ Registra el blueprint que contiene /tareas/crear

            if "panel_chat" in modulos:
                safe_register_blueprint(app, panel_chat_bp, url_prefix=f"/panel_cliente/{nombre_nora}/panel_chat")

            if "meta_ads" in modulos:
                # from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                # safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                pass  # Registro deshabilitado por error de import

            # Registrar solo si es meta_ads, no mezclar con ads (Google)
            if "meta_ads" in modulos:
                print(f"Registrando blueprint META ADS para {nombre_nora}")
                safe_register_blueprint(app, panel_cliente_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                # Registrar reportes avanzados de Meta Ads
                safe_register_blueprint(app, reportes_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                # Registrar estadísticas de Meta Ads SOLO con url_prefix=''
                # Cargar estadísticas de forma lazy
                estadisticas_bp = get_estadisticas_bp()
                if estadisticas_bp:
                    safe_register_blueprint(app, estadisticas_bp)

                # Registrar campañas avanzadas de Meta Ads
                from clientes.aura.routes.campanas_meta_ads import campanas_meta_ads_bp
                safe_register_blueprint(app, campanas_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")

            if "meta_ads" in modulos:
                from clientes.aura.routes.sincronizar_meta_ads import panel_cliente_meta_ads_bp
                safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")

            if "meta_ads" in modulos:
                from clientes.aura.routes.reportes_meta_ads.vista_sincronizacion import panel_cliente_meta_ads_sincronizacion_bp
                safe_register_blueprint(app, panel_cliente_meta_ads_sincronizacion_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")

            # ✅ Registro de Google Ads siguiendo el patrón de Meta Ads
            if "google_ads" in modulos:
                print(f"Registrando blueprint GOOGLE ADS para {nombre_nora}")
                safe_register_blueprint(app, panel_cliente_google_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/google_ads")

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

            if "cursos" in modulos:
                print(f"Registrando blueprint CURSOS para {nombre_nora}")
                safe_register_blueprint(app, panel_cliente_cursos_bp, url_prefix="")

            # ✅ Registro del módulo WhatsApp Web integrado (WebSocket)
            if "qr_whatsapp_web" in modulos:
                print(f"Registrando blueprint QR WHATSAPP WEB WEBSOCKET para {nombre_nora}")
                try:
                    from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_websocket import panel_cliente_whatsapp_web_bp
                    safe_register_blueprint(app, panel_cliente_whatsapp_web_bp, url_prefix=f'/panel_cliente/{nombre_nora}/whatsapp')
                    print(f"✅ Blueprint WhatsApp Web WebSocket registrado exitosamente")
                except Exception as e:
                    print(f"❌ Error registrando blueprint WhatsApp Web WebSocket: {e}")
                    # Fallback al blueprint original si el WebSocket falla
                    try:
                        from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_web_fixed import panel_cliente_whatsapp_web_bp
                        safe_register_blueprint(app, panel_cliente_whatsapp_web_bp, url_prefix=f'/panel_cliente/{nombre_nora}/whatsapp')
                        print(f"✅ Blueprint WhatsApp Web original registrado como fallback")
                    except Exception as e2:
                        print(f"❌ Error también con blueprint original: {e2}")
                        import traceback
                        traceback.print_exc()

            # ✅ Conocimiento ahora está integrado en el panel de entrenamiento de admin_nora
            # if "conocimiento" in modulos:
            #     safe_register_blueprint(app, panel_cliente_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/conocimiento")
            #     safe_register_blueprint(app, panel_cliente_etiquetas_conocimiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/etiquetas_conocimiento")
            
            # Registrar módulo Meta Ads si está activo
            if "meta_ads" in modulos:
                # from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                # safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                pass  # Registro deshabilitado por error de import

            if "login" in modulos:
                # login_bp se registra en otro lugar - comentado para evitar error
                # safe_register_blueprint(app, login_bp, url_prefix=f"/login")
                pass

            # ✅ Diagnóstico detallado de módulos y rutas registradas

            modulos_url_esperada = {
                "pagos": f"/panel_cliente/{nombre_nora}/pagos",
                "tareas": f"/panel_cliente/{nombre_nora}/tareas",
                "etiquetas": f"/panel_cliente/{nombre_nora}/etiquetas",
                "conocimiento": f"/panel_cliente/{nombre_nora}/conocimiento",
                "panel_chat": f"/panel_cliente/{nombre_nora}/panel_chat",
                "meta_ads": f"/panel_cliente/{nombre_nora}/meta_ads",
                "google_ads": f"/panel_cliente/{nombre_nora}/google_ads",
                "ads": f"/panel_cliente/{nombre_nora}/ads",
                "clientes": f"/panel_cliente/{nombre_nora}/clientes",
                "cursos": f"/panel_cliente/{nombre_nora}/cursos",
                "whatsapp": f"/panel_cliente/{nombre_nora}/whatsapp",
                "qr_whatsapp_web": f"/panel_cliente/{nombre_nora}/whatsapp"
            }

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

    # Mostrar rutas y endpoints relacionados con google_ads
    print("\n🧪 Rutas registradas relacionadas con google_ads:")
    for rule in app.url_map.iter_rules():
        if 'google_ads' in rule.rule or 'google_ads' in rule.endpoint:
            print(f"  - {rule.rule} → {rule.endpoint}")
