# ✅ Archivo: clientes/aura/routes/login.py
# 👉 Maneja claramente 3 tipos de usuarios (admin, cliente, usuarios_clientes)

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from supabase import create_client
from requests_oauthlib import OAuth2Session
import os
import json  # asegúrate que está al inicio del archivo

login_bp = Blueprint("login", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

print("🔁 REDIRECT_URI en uso:", REDIRECT_URI)

# 🔑 Correos admin generales desde .env
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")

def get_google_auth(token=None, state=None):
    if token:
        return OAuth2Session(GOOGLE_CLIENT_ID, token=token)
    if state:
        return OAuth2Session(GOOGLE_CLIENT_ID, state=state, redirect_uri=REDIRECT_URI)

    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]
    return OAuth2Session(GOOGLE_CLIENT_ID, scope=scope, redirect_uri=REDIRECT_URI)

@login_bp.route("/")
def login():
    return render_template("login.html")

@login_bp.route("/start")
def login_start():
    if os.getenv("MODO_DEV") == "True":
        session["email"] = "bluetiemx@gmail.com"
        session["name"] = "Super Luica"
        session["is_admin"] = True
        session["nombre_nora"] = "aura"
        session["usuario_empresa_id"] = "00000000-0000-0000-0000-000000000000"
        session["user"] = {
            "id": "00000000-0000-0000-0000-000000000000",
            "nombre": "Super Luica",
            "nombre_nora": "aura",
            "empresa_id": "0000-empresa-fake",
            "cliente_id": "0000-cliente-fake"
        }
        return redirect("/admin")  # ✅ Ir al panel de admin, no al cliente

    # Si no estás en modo dev, continúa con el flujo real de Google OAuth
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        access_type="offline", prompt="select_account")
    session["state"] = state
    return redirect(auth_url)

@login_bp.route("/google/callback")
def login_callback():
    try:
        google = get_google_auth(state=session.get("state"))
        token = google.fetch_token(
            "https://accounts.google.com/o/oauth2/token",
            client_secret=GOOGLE_CLIENT_SECRET,
            authorization_response=request.url,
        )
        session["token"] = token
        google = get_google_auth(token=token)
        resp = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
        user_info = resp.json()

        correo = user_info.get("email")
        session.permanent = True  # 🔐 mantiene la sesión activa

        # 🟢 Primero: Validar admin general desde .env
        if correo in ADMIN_EMAILS:
            session["email"] = correo
            session["name"] = user_info.get("name")
            session["is_admin"] = True
            session["nombre_nora"] = "admin"
            return redirect(url_for("admin_dashboard.dashboard_admin"))

        # 🔵 Segundo: Validar cliente desde configuracion_bot
        result_cliente = supabase.table("configuracion_bot").select("*").eq("correo_cliente", correo).execute()

        if result_cliente.data:
            datos = result_cliente.data[0]

            session["email"] = correo
            session["name"] = datos.get("nombre", user_info.get("name"))
            session["is_admin"] = str(datos.get("tipo_usuario", "")).lower() == "admin"
            session["nombre_nora"] = datos["nombre_nora"]

            session["user"] = {
                "id": datos.get("id", ""),
                "nombre": datos.get("nombre", "Desconocido"),
                "nombre_nora": datos.get("nombre_nora", ""),
                "empresa_id": datos.get("empresa_id", ""),
                "cliente_id": datos.get("cliente_id", "")
            }
            session["usuario_empresa_id"] = datos.get("id", "")

            return redirect(url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=session["nombre_nora"]))

        # 🟡 Tercero: Validar usuarios_clientes (empleados)
        result_empleado = supabase.table("usuarios_clientes").select("*").eq("correo", correo).execute()

        if result_empleado.data:
            datos_empleado = result_empleado.data[0]

            session["email"] = correo
            session["name"] = datos_empleado.get("nombre", user_info.get("name"))
            session["is_admin"] = False  # ← Fuerza que NO tenga acceso admin
            session["nombre_nora"] = datos_empleado["nombre_nora"]
            session["usuario_empresa_id"] = datos_empleado.get("id", "")

            session["user"] = {
                "id": datos_empleado.get("id", ""),
                "nombre": datos_empleado.get("nombre", "Desconocido"),
                "nombre_nora": datos_empleado.get("nombre_nora", ""),
                "empresa_id": datos_empleado.get("empresa_id", ""),
                "cliente_id": datos_empleado.get("cliente_id", "")
            }

            return redirect(f"/panel_team/{session['nombre_nora']}")

        # 🔴 Si no está en ninguna tabla, mostrar error
        return "❌ Este correo no tiene acceso autorizado.", 403

    except Exception as e:
        return f"Error en login: {str(e)}"

# 👉 Login alternativo por Supabase (correo + contraseña)

@login_bp.route("/login/supabase", methods=["GET"])
def supabase_login_form():
    return render_template("login_supabase.html")  # lo crearemos enseguida

@login_bp.route("/login/supabase/validar", methods=["POST"])
def supabase_login_validar():
    correo = request.form.get("correo")
    password = request.form.get("password")

    # 🔍 Buscar en super_admins
    res_admin = supabase.table("super_admins").select("*").eq("correo", correo).eq("activo", True).execute()
    if res_admin.data:
        admin = res_admin.data[0]
        if str(admin.get("password", "")) == password:
            session["email"] = correo
            session["name"] = admin.get("nombre", "Admin")
            session["is_admin"] = True
            session["nombre_nora"] = "admin"
            session["usuario_empresa_id"] = "00000000-0000-0000-0000-000000000000"
            session["user"] = {
                "id": admin.get("id"),
                "nombre": admin.get("nombre", "Admin"),
                "nombre_nora": "admin",
                "empresa_id": "admin",
                "cliente_id": "admin"
            }
            return redirect("/admin")

    # 🔍 Buscar en usuarios_clientes
    res_user = supabase.table("usuarios_clientes").select("*").eq("correo", correo).execute()
    if res_user.data:
        user = res_user.data[0]
        if str(user.get("password", "")) == password:
            session["email"] = correo
            session["name"] = user.get("nombre", "Cliente")
            session["is_admin"] = False
            session["nombre_nora"] = user.get("nombre_nora", "aura")
            session["usuario_empresa_id"] = user.get("id", "")
            session["user"] = {
                "id": user.get("id"),
                "nombre": user.get("nombre"),
                "nombre_nora": user.get("nombre_nora", "aura"),
                "empresa_id": user.get("empresa_id", ""),
                "cliente_id": user.get("cliente_id", "")
            }
            return redirect(f"/panel_cliente/{session['nombre_nora']}/tareas/gestionar")

    flash("❌ Correo o contraseña incorrectos")
    return redirect(url_for("login.supabase_login_form"))
