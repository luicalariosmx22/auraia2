
import importlib
from supabase import create_client
from dotenv import load_dotenv
import os
import json

# Importaciones base de blueprints
from clientes.aura.routes.panel_cliente import crear_blueprint_panel_cliente
from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
from clientes.aura.routes.panel_cliente_envios import panel_cliente_envios_bp
from clientes.aura.routes.panel_cliente_ia import panel_cliente_ia_bp
from clientes.aura.routes.panel_cliente_respuestas import panel_cliente_respuestas_bp
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_cliente_clientes import panel_cliente_clientes_bp
from clientes.aura.routes.panel_cliente_tareas import panel_cliente_tareas_bp
from clientes.aura.routes.panel_cliente_cursos import panel_cliente_cursos_bp
from clientes.aura.routes.panel_cliente_whatsapp_web import panel_cliente_whatsapp_web_bp
from clientes.aura.routes.webhook_contactos import webhook_contactos_bp
from clientes.aura.routes.panel_team.vista_panel_team import panel_team_bp
from clientes.aura.routes.panel_cliente_tareas.recurrentes import panel_tareas_recurrentes_bp
from clientes.aura.routes.panel_cliente_google_ads import panel_cliente_google_ads_bp
from clientes.aura.routes.whatsapp_integration import whatsapp_integration_bp
from clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
# Imports adicionales (movidos desde los bloques condicionales)
from clientes.aura.routes.panel_cliente_entrenamiento.vista_panel_cliente_entrenamiento import panel_cliente_entrenamiento_bp
from clientes.aura.routes.panel_cliente_tareas.gestionar import panel_tareas_gestionar_bp
from clientes.aura.routes.panel_cliente_tareas.tareas_crud import panel_tareas_crud_bp
from clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
# El módulo de WhatsApp Web Websocket requiere importación dinámica debido a conflictos de nombre
# from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_websocket import panel_cliente_whatsapp_web_bp

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_modulos_activos(nombre_nora):
    try:
        modulos_activados = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', nombre_nora).single().execute()
        return modulos_activados.data["modulos"] if modulos_activados.data else []
    except Exception as e:
        print(f"❌ Error al obtener módulos activos para {nombre_nora}: {e}")
        return []

def safe_register_blueprint(app, blueprint, **kwargs):
    if blueprint.name not in app.blueprints:
        app.register_blueprint(blueprint, **kwargs)
        print(f"✅ Blueprint '{blueprint.name}' registrado con prefijo '{kwargs.get('url_prefix', '')}'")
    else:
        print(f"⚠️ Blueprint '{blueprint.name}' ya estaba registrado.")

def registrar_modulo(app, nombre_modulo, blueprint, ruta, modulos_registrados):
    """
    Registra un módulo (blueprint) con manejo de errores.
    
    Args:
        app: La aplicación Flask
        nombre_modulo (str): Nombre del módulo a registrar
        blueprint: Blueprint de Flask a registrar
        ruta (str): Prefijo URL para el blueprint
        modulos_registrados (set): Conjunto donde registrar módulos exitosos
        
    Returns:
        bool: True si se registró correctamente, False en caso de error
    """
    try:
        safe_register_blueprint(app, blueprint, url_prefix=ruta)
        print(f"✅ Módulo de {nombre_modulo} registrado")
        modulos_registrados.add(nombre_modulo)
    except Exception as e:
        print(f"❌ Error al registrar módulo de {nombre_modulo}: {e}")
        import traceback
        traceback.print_exc()
        return False
    return True

def registrar_blueprints_por_nora(app, nombre_nora, safe_register_blueprint):
    """
    Registra los blueprints específicos para una Nora.
    
    Args:
        app: La aplicación Flask
        nombre_nora: Nombre de la Nora
        safe_register_blueprint: Función para registrar blueprints de forma segura
    """
    try:
        # Obtener los módulos activos
        modulos = obtener_modulos_activos(nombre_nora)
        
        # Guardamos qué módulos fueron registrados exitosamente
        modulos_registrados = set()

        # 1. MÓDULOS BASE (siempre se registran)
        # Panel cliente base
        bp = crear_blueprint_panel_cliente(nombre_nora)
        safe_register_blueprint(app, bp, url_prefix=f"/panel_cliente/{nombre_nora}")

        # Módulo de entrenamiento
        safe_register_blueprint(app, panel_cliente_entrenamiento_bp, url_prefix=f"/panel_cliente/{nombre_nora}/entrenamiento")

        # Webhook base
        safe_register_blueprint(app, webhook_contactos_bp, url_prefix="/")

        # 2. MÓDULOS CONDICIONALES
        # Contactos
        if "contactos" in modulos:
            registrar_modulo(app, "contactos", panel_cliente_contactos_bp, f"/panel_cliente/{nombre_nora}/contactos", modulos_registrados)
        
        # Pagos - requiere importación dinámica
        if "pagos" in modulos:
            try:
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
                print(f"✅ Módulo de pagos registrado")
                modulos_registrados.add("pagos")
            except Exception as e:
                print(f"❌ Error al registrar módulo de pagos: {e}")
                import traceback
                traceback.print_exc()

        # Tareas
        if "tareas" in modulos:
            try:
                safe_register_blueprint(app, panel_cliente_tareas_bp, url_prefix=f"/panel_cliente/{nombre_nora}/tareas")
                safe_register_blueprint(app, panel_tareas_gestionar_bp)
                safe_register_blueprint(app, panel_tareas_recurrentes_bp)
                safe_register_blueprint(app, panel_tareas_crud_bp)
                print(f"✅ Módulo de tareas registrado")
                modulos_registrados.add("tareas")
            except Exception as e:
                print(f"❌ Error al registrar módulo de tareas: {e}")
                import traceback
                traceback.print_exc()

        # Meta Ads
        if "meta_ads" in modulos:
            try:
                print(f"🔄 Registrando blueprint META ADS para {nombre_nora}")
                from clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
                safe_register_blueprint(app, panel_cliente_meta_ads_bp, url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
                print(f"✅ Módulo de Meta Ads registrado")
                modulos_registrados.add("meta_ads")
            except Exception as e:
                print(f"❌ Error al registrar módulo de Meta Ads: {e}")
                import traceback
                traceback.print_exc()

        # Google Ads
        if "google_ads" in modulos:
            registrar_modulo(app, "google_ads", panel_cliente_google_ads_bp, f"/panel_cliente/{nombre_nora}/google_ads", modulos_registrados)

        # Módulos básicos restantes - usando la nueva función registrar_modulo
        if "envios" in modulos:
            registrar_modulo(app, "envios", panel_cliente_envios_bp, f"/panel_cliente/{nombre_nora}/envios", modulos_registrados)
                
        if "ia" in modulos:
            registrar_modulo(app, "ia", panel_cliente_ia_bp, f"/panel_cliente/{nombre_nora}/ia", modulos_registrados)
                
        if "respuestas" in modulos:
            registrar_modulo(app, "respuestas", panel_cliente_respuestas_bp, f"/panel_cliente/{nombre_nora}/respuestas", modulos_registrados)
                
        if "clientes" in modulos:
            registrar_modulo(app, "clientes", panel_cliente_clientes_bp, f"/panel_cliente/{nombre_nora}/clientes", modulos_registrados)
                
        if "cursos" in modulos:
            registrar_modulo(app, "cursos", panel_cliente_cursos_bp, f"/panel_cliente/{nombre_nora}/cursos", modulos_registrados)

        # WhatsApp Web WebSocket - requiere importación dinámica debido a conflicto de nombres
        if "qr_whatsapp_web" in modulos:
            try:
                print(f"🔄 Registrando QR WHATSAPP WEB para {nombre_nora}")
                from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_websocket import panel_cliente_whatsapp_web_bp as whatsapp_websocket_bp
                safe_register_blueprint(app, whatsapp_websocket_bp, url_prefix=f'/panel_cliente/{nombre_nora}/whatsapp')
                print(f"✅ Blueprint WhatsApp Web registrado exitosamente")
                modulos_registrados.add("qr_whatsapp_web")
            except Exception as e:
                print(f"❌ Error al registrar módulo de WhatsApp Web: {e}")
                import traceback
                traceback.print_exc()

        # 3. MÓDULOS DINÁMICOS (generados por el creador)
        resultado = supabase.table("modulos_disponibles").select("nombre, ruta").execute()
        modulos_disponibles = resultado.data if resultado.data else []

        for item in modulos_disponibles:
            nombre_modulo = item["nombre"]
            ruta_import = item["ruta"]

            # Evita registrar dos veces el mismo módulo
            if nombre_modulo in modulos_registrados:
                continue

            try:
                if not ruta_import:
                    print(f"⚠️ Módulo '{nombre_modulo}' no tiene ruta definida")
                    continue

                # Soporta rutas en subcarpetas como 'panel_cliente_alertas.panel_cliente_alertas_bp'
                ruta_modulo = ruta_import.rsplit(".", 1)[0]  # Ej: 'panel_cliente_alertas'
                nombre_blueprint = ruta_import.split(".")[-1]  # Ej: 'panel_cliente_alertas_bp'

                # Importa correctamente incluso si está en subcarpeta
                modulo_importado = importlib.import_module(f"clientes.aura.routes.{ruta_modulo}")
                blueprint = getattr(modulo_importado, nombre_blueprint)

                ruta_url = f"/panel_cliente/{nombre_nora}/{nombre_modulo}"
                registrar_modulo(app, nombre_modulo, blueprint, ruta_url, modulos_registrados)

            except Exception as e:
                print(f"❌ Error al registrar módulo dinámico '{nombre_modulo}': {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos para {nombre_nora}: {e}")
        import traceback
        traceback.print_exc()
