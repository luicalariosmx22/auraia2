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
    try:
        total, cuentas = listar_cuentas_publicitarias()
        cuentas = cuentas or []
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[DEV] Total cuentas encontradas (sincronizar): {total}")
            logging.debug(f"[DEV] Resource names (sincronizar): {cuentas}")
    except Exception as e:
        cuentas = []
        mensaje = f"Error al obtener cuentas: {e}"
        if os.getenv("MODO_DEV", "False").lower() == "true":
            logging.exception("[DEV] Error buscando cuentas Google Ads en sincronizar")
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        # Obtener el token de entorno
        oauth_token = os.getenv("GOOGLE_CLIENT_SECRET")
        if customer_id and oauth_token:
            mensaje = f"Cuenta {customer_id} sincronizada correctamente usando token de entorno (demo)."
        else:
            mensaje = "Faltan datos para sincronizar o token no disponible."
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
                top_keywords=[]
            )

        # Inicializar cliente de Supabase y logging
        supabase_client = SupabaseGoogleAdsClient()
        logging.debug(f"Generando reporte para {nombre_nora} y empresa {empresa_id}")
        
        # Obtener estadísticas generales
        stats = supabase_client.calcular_estadisticas(nombre_nora, empresa_id)
        logging.debug(f"Estadísticas: {stats}")
        
        # Obtener datos de las campañas
        campanas = supabase_client.obtener_campanas(nombre_nora, empresa_id)
        logging.debug(f"Total campañas encontradas: {len(campanas)}")
        
        # Obtener datos de los anuncios
        anuncios = supabase_client.obtener_anuncios(nombre_nora, empresa_id)
        logging.debug(f"Total anuncios encontrados: {len(anuncios)}")
        
        # Obtener datos de las palabras clave
        keywords = supabase_client.obtener_palabras_clave(nombre_nora, empresa_id)
        logging.debug(f"Total keywords encontradas: {len(keywords)}")
        
        # Verificar si hay datos
        if not campanas and not anuncios and not keywords:
            flash("No se encontraron datos para mostrar. Asegúrate de haber sincronizado tu cuenta de Google Ads.", "warning")
        
        # Obtener top 5 campañas
        top_campanas = []
        if campanas:
            top_campanas = sorted(campanas, 
                                key=lambda x: float(x.get('impresiones', 0)), 
                                reverse=True)[:5]
        
        # Procesar estados de anuncios
        estados_anuncios = {}
        for anuncio in anuncios:
            estado = anuncio.get('estado', 'Desconocido')
            estados_anuncios[estado] = estados_anuncios.get(estado, 0) + 1
            
        if not estados_anuncios:
            estados_anuncios = {'Sin datos': 1}                # Obtener top 10 keywords
        top_keywords = []
        for kw in sorted(keywords, 
                        key=lambda x: float(x.get('impresiones', 0)), 
                        reverse=True)[:10]:
            impresiones = float(kw.get('impresiones', 0))
            clics = float(kw.get('clics', 0))
            ctr = (clics / impresiones) * 100 if impresiones > 0 else 0
            top_keywords.append({
                'keyword': kw.get('palabra_clave', ''),
                'ctr': round(ctr, 2),
                'impresiones': float(kw.get('impresiones', 0))
            })
        
        # Obtener la empresa actual
        empresa_actual = next((e for e in empresas if e['id'] == empresa_id), None)
        
        logging.debug("Renderizando template con datos procesados")
        return render_template(
            "panel_cliente_google_ads/reporte.html",
            nombre_nora=nombre_nora,
            empresas=empresas,
            empresa_id=empresa_id,
            empresa_actual=empresa_actual,
            stats=stats,
            top_campanas=top_campanas,
            estados_anuncios=estados_anuncios,
            top_keywords=top_keywords
        )
        
    except Exception as e:
        logging.exception("Error al generar reporte de Google Ads")
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
