# clientes/aura/auth/google_login.py

from flask import Blueprint, redirect, request, session, url_for, flash
from requests_oauthlib import OAuth2Session
from clientes.aura.utils.supabase_client import supabase
import os

google_login_bp = Blueprint("google_login", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

def verificar_usuario_google(email):
    """
    Verifica si el usuario de Google existe en usuarios_clientes
    """
    try:
        response = supabase.table("usuarios_clientes") \
            .select("*") \
            .eq("correo", email) \
            .eq("activo", True) \
            .execute()
        
        if response.data:
            usuario = response.data[0]
            print(f"✅ Usuario Google encontrado en BD: {usuario['nombre']}")
            return usuario
        else:
            print(f"❌ Usuario Google no autorizado: {email}")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando usuario Google: {e}")
        return None

def es_administrador_google(usuario):
    """
    Verifica si el usuario es administrador basado en rol y permisos
    """
    if not usuario:
        return False
    
    # Verificar rol de admin o supervisor
    rol = usuario.get("rol", "").lower()
    if rol in ["admin", "administrador", "interno"]:  # 🆕 Agregado "interno"
        return True
    
    if usuario.get("es_supervisor") or usuario.get("es_supervisor_tareas"):
        return True
    
    # Verificar módulos - puede ser lista o dict
    modulos = usuario.get("modulos", [])
    
    # Si modulos es una lista, verificar si contiene módulos de admin
    if isinstance(modulos, list):
        modulos_admin = ["admin", "administracion", "configuracion", "usuarios"]
        for modulo in modulos:
            if modulo.lower() in modulos_admin:
                return True
    
    # Si modulos es un dict, verificar permisos de admin
    elif isinstance(modulos, dict):
        for modulo, permisos in modulos.items():
            if isinstance(permisos, dict) and permisos.get("admin", False):
                return True
    
    return False

@google_login_bp.route("/login")
def login():
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

    authorization_url, state = oauth.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="select_account"
    )

    session["oauth_state"] = state
    return redirect(authorization_url)

@google_login_bp.route("/login/google/callback")
def callback():
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        state=session.get("oauth_state")
    )

    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url,
    )

    resp = oauth.get(USER_INFO_URL)
    user_info = resp.json()
    
    email = user_info.get("email")
    nombre_google = user_info.get("name")
    
    # Verificar usuario en base de datos
    usuario = verificar_usuario_google(email)
    if not usuario:
        flash(f"❌ Usuario {email} no autorizado en el sistema", "error")
        return redirect(url_for("simple_login.login_simple"))
    
    # Establecer sesión con datos de BD + Google
    session.permanent = True
    session["email"] = usuario["correo"]
    session["name"] = usuario["nombre"]  # Usar nombre de BD
    session["nombre_nora"] = usuario.get("nombre_nora", "aura")
    session["is_admin"] = es_administrador_google(usuario)
    session["user"] = {
        "id": usuario["id"],
        "email": usuario["correo"],
        "nombre": usuario["nombre"],
        "nombre_nora": usuario.get("nombre_nora", "aura"),
        "rol": usuario.get("rol", "cliente"),
        "modulos": usuario.get("modulos", {}),
        "es_supervisor": usuario.get("es_supervisor", False),
        "picture": user_info.get("picture"),  # Foto de Google
        "google_id": user_info.get("id")      # ID de Google
    }
    session.modified = True
    
    print(f"🔐 Google Login exitoso para {usuario['correo']}")
    print(f"📊 Permisos: Admin={es_administrador_google(usuario)}, Rol={usuario.get('rol')}")
    
    flash(f"✅ Bienvenido {usuario['nombre']} (Google)", "success")

    # Redirigir según permisos
    if es_administrador_google(usuario):
        return redirect("/admin")
    else:
        nombre_nora = usuario.get("nombre_nora", "aura")
        return redirect(f"/panel_cliente/{nombre_nora}/entrenar")
