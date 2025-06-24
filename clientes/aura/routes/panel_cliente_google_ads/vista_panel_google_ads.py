from flask import render_template, request, redirect, url_for, flash
from clientes.aura.utils.permisos import obtener_permisos
import os
from dotenv import load_dotenv
import logging
from .listar_cuentas import listar_cuentas_publicitarias
from flask import redirect, session, url_for
from google_auth_oauthlib.flow import InstalledAppFlow, Flow

# No redefinas blueprint aquí, solo usa el del archivo contenedor
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp

# Cargar variables de entorno desde .env.local si existe
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local'))

@panel_cliente_google_ads_bp.route("/", methods=["GET", "POST"], strict_slashes=False)
def index_google_ads():
    # Extrae nombre_nora desde el prefijo de la URL
    nombre_nora = request.view_args.get("nombre_nora")
    sincronizado = None
    if request.method == "POST":
        # Aquí iría la lógica real de sincronización con Google Ads
        sincronizado = "¡Cuentas publicitarias sincronizadas exitosamente! (demo)"
    permisos = obtener_permisos()
    return render_template("panel_cliente_google_ads/index.html", nombre_nora=nombre_nora, permisos=permisos, sincronizado=sincronizado)

@panel_cliente_google_ads_bp.route("/sincronizar", methods=["GET", "POST"], strict_slashes=False)
def sincronizar_google_ads():
    nombre_nora = request.view_args.get("nombre_nora")
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

# Cambia la ruta para que acepte el parámetro nombre_nora en la URL
@panel_cliente_google_ads_bp.route("/panel_cliente/<nombre_nora>/google_ads/autorizar", methods=["GET"], strict_slashes=False)
def autorizar_google_ads(nombre_nora):
    import google_auth_oauthlib
    print("[DEBUG] google-auth-oauthlib version:", google_auth_oauthlib.__version__)
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "https://app.soynoraai.com/panel_cliente/aura/google_ads/oauth_callback"

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
        scopes=["https://www.googleapis.com/auth/adwords"],
        redirect_uri=redirect_uri
    )

    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )

    session["google_ads_state"] = flow.state
    session["nombre_nora"] = nombre_nora

    return redirect(auth_url)

@panel_cliente_google_ads_bp.route("/oauth_callback", methods=["GET"], strict_slashes=False)
def google_ads_oauth_callback():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "https://app.soynoraai.com/panel_cliente/aura/google_ads/oauth_callback"

    state = session.get("google_ads_state")
    nombre_nora = session.get("nombre_nora")
    if not state:
        return "❌ Estado inválido. Inicia el flujo de autorización desde /autorizar", 400

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/adwords"],
        state=state,
        redirect_uri=redirect_uri
    )

    flow.fetch_token(authorization_response=request.url)
    refresh_token = flow.credentials.refresh_token

    return f"""
    <h2>✅ Refresh Token generado con éxito</h2>
    <p>Agrega esto a tu archivo <code>.env.local</code>:</p>
    <pre>GOOGLE_REFRESH_TOKEN={refresh_token}</pre>
    <p><strong>Luego reinicia tu servidor en Railway.</strong></p>
    <p>Volver a <a href='/panel_cliente/{nombre_nora}/google_ads/autorizar'>autorizar Google Ads</a></p>
    """
