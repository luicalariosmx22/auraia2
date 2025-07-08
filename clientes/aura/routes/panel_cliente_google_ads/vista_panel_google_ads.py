# ✅ Archivo: clientes/aura/routes/panel_cliente_google_ads/vista_panel_google_ads.py
# 👉 Vistas para autorizar Google Ads con OAuth, soportando múltiples usuarios (nombre_nora)

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from clientes.aura.utils.permisos import obtener_permisos
from clientes.aura.utils.supabase_client import supabase
import os
from dotenv import load_dotenv
import logging
from .listar_cuentas import listar_cuentas_publicitarias
from google_auth_oauthlib.flow import Flow
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp
from clientes.aura.utils.supabase_google_ads_client import SupabaseGoogleAdsClient
from clientes.aura.services.google_ads_service import google_ads_service

# Cargar variables de entorno desde .env.local si existe
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local'))

def obtener_empresas(nombre_nora):
    """
    Obtiene la lista de empresas disponibles para el usuario desde la tabla cliente_empresas
    """
    try:
        response = supabase.table('cliente_empresas') \
            .select('id, nombre_empresa as nombre') \
            .eq('nombre_nora', nombre_nora) \
            .eq('activo', True) \
            .execute()
        return response.data if response else []
    except Exception as e:
        logging.error(f"Error al obtener empresas: {str(e)}")
        return []

@panel_cliente_google_ads_bp.route("/", methods=["GET", "POST"], strict_slashes=False)
def index_google_ads(nombre_nora):
    # Obtener lista de empresas
    empresas = obtener_empresas(nombre_nora)
    
    # Obtener empresa seleccionada de la sesión
    empresa_id = session.get(f'google_ads_empresa_{nombre_nora}')
    
    sincronizado = None
    if request.method == "POST":
        # Aquí iría la lógica real de sincronización con Google Ads
        sincronizado = "¡Cuentas publicitarias sincronizadas exitosamente! (demo)"
    permisos = obtener_permisos()
    return render_template(
        "panel_cliente_google_ads/index.html",
        nombre_nora=nombre_nora,
        permisos=permisos,
        sincronizado=sincronizado,
        empresas=empresas,
        empresa_id=empresa_id
    )

@panel_cliente_google_ads_bp.route("/sincronizar", methods=["GET", "POST"], strict_slashes=False)
def sincronizar_google_ads(nombre_nora):
    mensaje = None
    cuentas = []
    
    try:
        # Usar el nuevo servicio de Google Ads
        total, cuentas_ads = google_ads_service.listar_cuentas_accesibles()
        cuentas = cuentas_ads or []
        
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[DEV] Total cuentas encontradas (sincronizar): {total}")
            logging.debug(f"[DEV] Cuentas encontradas: {[c['nombre'] for c in cuentas]}")
            
    except Exception as e:
        cuentas = []
        mensaje = f"Error al obtener cuentas de Google Ads: {str(e)}"
        logging.exception("[DEV] Error buscando cuentas Google Ads en sincronizar")
    
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        if customer_id and cuentas:
            # Encontrar la cuenta seleccionada
            cuenta_seleccionada = next((c for c in cuentas if c['id'] == customer_id), None)
            if cuenta_seleccionada:
                mensaje = f"✅ Cuenta '{cuenta_seleccionada['nombre']}' ({customer_id}) lista para usar con datos reales de Google Ads."
            else:
                mensaje = "❌ Cuenta no encontrada en la lista de cuentas accesibles."
        else:
            mensaje = "❌ Faltan datos para sincronizar o no hay cuentas disponibles."
    
    return render_template(
        "panel_cliente_google_ads/sincronizar.html",
        nombre_nora=nombre_nora,
        cuentas=cuentas,
        mensaje=mensaje
    )

# --- FLUJO OAUTH GOOGLE ADS ---
# Esta ruta inicia el flujo OAuth. El redirect_uri es dinámico y depende de nombre_nora.
@panel_cliente_google_ads_bp.route("/autorizar", methods=["GET", "POST"], strict_slashes=False)
def autorizar_google_ads(nombre_nora):
    if not nombre_nora:
        return "❌ Error: nombre_nora no especificado en la URL.", 400
    # Si es GET, muestra el template de autorización
    if request.method == "GET":
        return render_template("panel_cliente_google_ads/autorizar.html", nombre_nora=nombre_nora)
    # Si es POST, inicia el flujo OAuth
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = url_for('panel_cliente_google_ads.google_ads_oauth_callback', nombre_nora=nombre_nora, _external=True)

    if not client_id or not client_secret:
        return "❌ Faltan CLIENT_ID o CLIENT_SECRET en .env.local", 500

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/adwords",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        redirect_uri=redirect_uri
    )

    auth_url, state = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )

    session["google_ads_state"] = state
    session["nombre_nora"] = nombre_nora

    return redirect(auth_url)

# Callback de Google: aquí se recibe el refresh_token y se muestra al usuario
@panel_cliente_google_ads_bp.route("/oauth_callback", methods=["GET"], strict_slashes=False)
def google_ads_oauth_callback(nombre_nora):
    import logging
    from google_auth_oauthlib.flow import Flow

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    redirect_uri = url_for("panel_cliente_google_ads.google_ads_oauth_callback", nombre_nora=nombre_nora, _external=True)

    # Logs de entrada
    logging.debug("🌀 Callback recibido desde Google OAuth")
    logging.debug("👉 request.args: %s", dict(request.args))
    logging.debug("👉 session: %s", dict(session))

    state = session.get("google_ads_state")
    if not state:
        return "❌ Estado inválido. Falta google_ads_state en la sesión", 400

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/adwords",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        state=state,
        redirect_uri=redirect_uri
    )

    try:
        flow.fetch_token(authorization_response=request.url)
        refresh_token = flow.credentials.refresh_token
        logging.info(f"✅ Refresh token generado para {nombre_nora}: {refresh_token}")
    except Exception as e:
        logging.exception("❌ Error al intercambiar código por token")
        return f"<h3>Error al completar el proceso de autorización</h3><pre>{str(e)}</pre>", 500

    return f"""
    <h2>✅ Token generado con éxito para <code>{nombre_nora}</code></h2>
    <p>Agrega esta línea en tu archivo <code>.env.local</code>:</p>
    <pre>GOOGLE_REFRESH_TOKEN={refresh_token}</pre>
    <p><strong>No olvides reiniciar Railway para que lo tome.</strong></p>
    """

@panel_cliente_google_ads_bp.route("/reporte", methods=["GET"], strict_slashes=False)
def reporte_google_ads(nombre_nora):
    try:
        # Obtener lista de empresas
        empresas = obtener_empresas(nombre_nora)
        
        # Obtener empresa_id de la sesión
        empresa_id = session.get(f'google_ads_empresa_{nombre_nora}')
        
        # Si no hay empresa seleccionada, mostrar la plantilla con el selector
        if not empresa_id:
            return render_template(
                "panel_cliente_google_ads/reporte.html",
                nombre_nora=nombre_nora,
                empresas=empresas,
                empresa_id=None,
                stats=None,
                top_campanas=[],
                estados_anuncios={},
                top_keywords=[],
                mensaje_info="Seleccione una empresa para ver el reporte de Google Ads"
            )

        # Obtener información de la empresa desde la base de datos
        try:
            response = supabase.table('cliente_empresas') \
                .select('*, google_ads_customer_id') \
                .eq('id', empresa_id) \
                .eq('nombre_nora', nombre_nora) \
                .single() \
                .execute()
            
            empresa_data = response.data if response else None
            customer_id = empresa_data.get('google_ads_customer_id') if empresa_data else None
            
        except Exception as e:
            logging.error(f"Error obteniendo datos de empresa: {e}")
            empresa_data = {"nombre": "Empresa no encontrada"}
            customer_id = None

        # Si no hay customer_id configurado, mostrar mensaje
        if not customer_id:
            return render_template(
                "panel_cliente_google_ads/reporte.html",
                nombre_nora=nombre_nora,
                empresas=empresas,
                empresa_id=empresa_id,
                empresa_actual=empresa_data,
                stats=None,
                top_campanas=[],
                estados_anuncios={},
                top_keywords=[],
                mensaje_warning="Esta empresa no tiene configurado un Customer ID de Google Ads. Configure uno en la sección de sincronización."
            )

        # Obtener datos reales de Google Ads
        logging.info(f"🔍 Obteniendo reporte real de Google Ads para customer_id: {customer_id}")
        
        try:
            # Usar el servicio integrado para obtener datos reales
            reporte_completo = google_ads_service.obtener_reporte_completo(customer_id, dias=30)
            
            # Extraer datos del reporte
            stats = reporte_completo["estadisticas_generales"]
            top_campanas = reporte_completo["top_campanas"]
            top_keywords = reporte_completo["top_keywords"]
            estados_anuncios = reporte_completo["distribucion_estados_anuncios"]
            
            # Procesar keywords para el formato esperado por la plantilla
            keywords_formateados = []
            for kw in top_keywords[:10]:  # Top 10
                keywords_formateados.append({
                    'keyword': kw['texto'],
                    'ctr': kw['ctr'],
                    'impresiones': kw['impresiones'],
                    'clics': kw['clics'],
                    'costo': kw['costo']
                })

            mensaje_exito = f"✅ Datos reales obtenidos de Google Ads para el período de {stats['periodo_dias']} días ({stats['fecha_inicio']} a {stats['fecha_fin']})"
            
            logging.info("✅ Reporte de Google Ads generado exitosamente con datos reales")
            
        except Exception as e:
            logging.exception(f"❌ Error obteniendo datos reales de Google Ads: {e}")
            
            # Fallback a datos de Supabase si falla la API
            supabase_client = SupabaseGoogleAdsClient()
            stats = supabase_client.calcular_estadisticas(nombre_nora, empresa_id)
            campanas = supabase_client.obtener_campanas(nombre_nora, empresa_id)
            anuncios = supabase_client.obtener_anuncios(nombre_nora, empresa_id)
            keywords = supabase_client.obtener_palabras_clave(nombre_nora, empresa_id)
            
            # Procesar datos de fallback
            top_campanas = sorted(campanas, key=lambda x: float(x.get('impresiones', 0)), reverse=True)[:5] if campanas else []
            
            estados_anuncios = {}
            for anuncio in anuncios:
                estado = anuncio.get('estado', 'Desconocido')
                estados_anuncios[estado] = estados_anuncios.get(estado, 0) + 1
            if not estados_anuncios:
                estados_anuncios = {'Sin datos': 1}
            
            keywords_formateados = []
            for kw in sorted(keywords, key=lambda x: float(x.get('impresiones', 0)), reverse=True)[:10]:
                impresiones = float(kw.get('impresiones', 0))
                clics = float(kw.get('clics', 0))
                ctr = (clics / impresiones) * 100 if impresiones > 0 else 0
                keywords_formateados.append({
                    'keyword': kw.get('palabra_clave', ''),
                    'ctr': round(ctr, 2),
                    'impresiones': impresiones,
                    'clics': clics,
                    'costo': float(kw.get('costo', 0))
                })
            
            mensaje_warning = f"⚠️ Error conectando con Google Ads API: {str(e)}. Mostrando datos almacenados localmente."

        return render_template(
            "panel_cliente_google_ads/reporte.html",
            nombre_nora=nombre_nora,
            empresas=empresas,
            empresa_id=empresa_id,
            empresa_actual=empresa_data,
            stats=stats,
            top_campanas=top_campanas,
            estados_anuncios=estados_anuncios,
            top_keywords=keywords_formateados,
            mensaje_exito=locals().get('mensaje_exito'),
            mensaje_warning=locals().get('mensaje_warning')
        )
        
    except Exception as e:
        logging.exception("Error general al generar reporte de Google Ads")
        return f"Error al generar reporte: {str(e)}", 500

@panel_cliente_google_ads_bp.route("/actualizar_empresa", methods=["POST"], strict_slashes=False)
def actualizar_empresa(nombre_nora):
    """
    Actualiza la empresa seleccionada en la sesión
    """
    try:
        data = request.get_json()
        empresa_id = data.get('empresa_id')
        if not empresa_id:
            return jsonify({"error": "empresa_id es requerido"}), 400
            
        # Guardar en la sesión
        session[f'google_ads_empresa_{nombre_nora}'] = empresa_id
        return jsonify({"message": "Empresa actualizada correctamente"}), 200
        
    except Exception as e:
        logging.error(f"Error al actualizar empresa: {str(e)}")
        return jsonify({"error": str(e)}), 500

@panel_cliente_google_ads_bp.route("/vincular_cuenta", methods=["POST"], strict_slashes=False)
def vincular_cuenta_google_ads(nombre_nora):
    """
    Vincula una cuenta de Google Ads (customer_id) con una empresa específica
    """
    try:
        data = request.get_json()
        empresa_id = data.get('empresa_id')
        customer_id = data.get('customer_id')
        
        if not empresa_id or not customer_id:
            return jsonify({"error": "empresa_id y customer_id son requeridos"}), 400
        
        # Validar que la cuenta de Google Ads existe y es accesible
        try:
            total, cuentas = google_ads_service.listar_cuentas_accesibles()
            account_exists = any(cuenta['id'] == customer_id for cuenta in cuentas)
            
            if not account_exists:
                return jsonify({"error": "La cuenta de Google Ads no existe o no es accesible"}), 400
                
        except Exception as e:
            return jsonify({"error": f"Error validando cuenta de Google Ads: {str(e)}"}), 500
        
        # Actualizar la empresa con el customer_id
        try:
            response = supabase.table('cliente_empresas') \
                .update({'google_ads_customer_id': customer_id}) \
                .eq('id', empresa_id) \
                .eq('nombre_nora', nombre_nora) \
                .execute()
            
            if response.data:
                return jsonify({
                    "message": "Cuenta de Google Ads vinculada exitosamente",
                    "customer_id": customer_id,
                    "empresa_id": empresa_id
                }), 200
            else:
                return jsonify({"error": "No se pudo actualizar la empresa"}), 500
                
        except Exception as e:
            logging.error(f"Error actualizando empresa: {str(e)}")
            return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
        
    except Exception as e:
        logging.error(f"Error vinculando cuenta: {str(e)}")
        return jsonify({"error": str(e)}), 500

@panel_cliente_google_ads_bp.route("/cuentas_disponibles", methods=["GET"], strict_slashes=False)
def obtener_cuentas_disponibles(nombre_nora):
    """
    Obtiene la lista de cuentas de Google Ads disponibles para vincular
    """
    try:
        total, cuentas = google_ads_service.listar_cuentas_accesibles()
        
        return jsonify({
            "total": total,
            "cuentas": cuentas
        }), 200
        
    except Exception as e:
        logging.error(f"Error obteniendo cuentas disponibles: {str(e)}")
        return jsonify({"error": str(e)}), 500
