from flask import render_template, request, redirect, url_for, flash
from clientes.aura.utils.permisos import obtener_permisos
import os
from dotenv import load_dotenv
import logging
from .listar_cuentas import listar_cuentas_publicitarias
from flask import redirect, session, url_for
from google_auth_oauthlib.flow import InstalledAppFlow

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

@panel_cliente_google_ads_bp.route("/autorizar", strict_slashes=False)
def autorizar_google_ads():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    # Solo permitir en modo desarrollo
    if os.getenv("MODO_DEV", "False").lower() != "true":
        return "❌ Esta ruta solo está permitida en modo desarrollo (MODO_DEV=True)", 403

    if not client_id or not client_secret:
        return "❌ Faltan CLIENT_ID o CLIENT_SECRET en .env.local", 500

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/adwords"],
    )

    creds = flow.run_local_server(port=8080, prompt="consent")

    refresh_token = creds.refresh_token
    print("✅ REFRESH TOKEN:", refresh_token)

    return f"""
    <h2>✅ Refresh Token generado con éxito</h2>
    <p>Copia y pega el siguiente valor en tu archivo <code>.env.local</code>:</p>
    <pre style=\"background:#f4f4f4;padding:1em;border-radius:5px;\">GOOGLE_REFRESH_TOKEN={refresh_token}</pre>
    <p><strong>Luego reinicia tu servidor para que se aplique correctamente.</strong></p>
    """
