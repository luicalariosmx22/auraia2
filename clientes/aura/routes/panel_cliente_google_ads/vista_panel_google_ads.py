# ✅ Archivo: clientes/aura/routes/panel_cliente_google_ads/vista_panel_google_ads.py
# 👉 Vistas para autorizar Google Ads con OAuth, soportando múltiples usuarios (nombre_nora)

from flask import render_template, request, redirect, url_for, flash, session
from clientes.aura.utils.permisos import obtener_permisos
import os
from dotenv import load_dotenv
import logging
from .listar_cuentas import listar_cuentas_publicitarias
from google_auth_oauthlib.flow import Flow
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

# --- FLUJO OAUTH GOOGLE ADS ---
# Esta ruta inicia el flujo OAuth. El redirect_uri es dinámico y depende de nombre_nora.
@panel_cliente_google_ads_bp.route("/autorizar", methods=["GET"], strict_slashes=False)
def autorizar_google_ads(nombre_nora):
    if not nombre_nora:
        return "❌ Error: nombre_nora no especificado en la URL.", 400
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
        scopes=["https://www.googleapis.com/auth/adwords"],
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
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = url_for('panel_cliente_google_ads.google_ads_oauth_callback', nombre_nora=nombre_nora, _external=True)

    state = session.get("google_ads_state")
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

    # Mostrar el refresh_token y un link para volver a autorizar
    return f"""
    <h2>✅ Refresh Token generado con éxito</h2>
    <p>Agrega esto a tu archivo <code>.env.local</code>:</p>
    <pre>GOOGLE_REFRESH_TOKEN={refresh_token}</pre>
    <p><strong>Luego reinicia tu servidor en Railway.</strong></p>
    <p>Volver a <a href='{url_for('panel_cliente_google_ads.autorizar_google_ads', nombre_nora=nombre_nora)}'>autorizar Google Ads</a></p>
    """
