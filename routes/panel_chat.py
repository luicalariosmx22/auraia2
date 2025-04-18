# routes/panel_chat.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os
import datetime
import openai
from clientes.aura.utils.normalizador import normalizar_numero

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

openai.api_key = os.getenv("OPENAI_API_KEY")

panel_chat_bp = Blueprint("panel_chat", __name__)

def leer_contactos():
    try:
        response = supabase.table("contactos").select("*").execute()
        return response.data or []
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return []

def leer_historial(telefono, limite=20, offset=0):
    telefono = normalizar_numero(telefono)
    numero_simplificado = telefono[-10:]
    try:
        print(f"🔍 Leyendo historial para: {telefono} (últimos {limite} desde offset {offset})")
        response = (
            supabase
            .table("historial_conversaciones")
            .select("*")
            .like("telefono", f"%{numero_simplificado}")
            .order("hora", desc=False)
            .range(offset, offset + limite - 1)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"❌ Error al cargar historial para {telefono}: {str(e)}")
        return []

def generar_resumen_ia(mensajes):
    if not mensajes:
        return "No hay suficientes mensajes para generar un resumen."

    texto = "\n".join([f"{m['emisor']}: {m['mensaje']}" for m in mensajes[-20:]])
    prompt = f"""
Eres un asistente profesional. Resume brevemente esta conversación entre un cliente y una IA llamada Nora. El resumen debe identificar si el cliente está interesado en algo, si ya fue atendido, y si hay seguimiento pendiente:

{texto}

Resumen:
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error al generar resumen con IA: {e}")
        return "No se pudo generar el resumen con IA."

# Ruta para el panel principal
@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    if "user" not in session:
        return redirect(url_for("google_login.login"))

    contactos = leer_contactos()
    lista = []
    for c in contactos:
        mensajes = leer_historial(c["telefono"], limite=10)  # Solo últimos 10 mensajes
        lista.append({**c, "mensajes": mensajes})

    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

# Ruta para obtener el historial de un contacto
@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    offset = int(request.args.get("offset", 0))  # 👈 ahora acepta offset por query param
    telefono = normalizar_numero(telefono)
    historial = leer_historial(telefono, limite=20, offset=offset)

    contacto = None
    contactos = leer_contactos()
    for c in contactos:
        if normalizar_numero(c["telefono"])[-10:] == telefono[-10:]:
            contacto = c
            break

    resumen = generar_resumen_ia(historial)
    return jsonify({
        "success": True,
        "contacto": contacto or {},
        "mensajes": historial,
        "resumen_ia": resumen
    })

# Ruta para el panel limitado (clientes)
@panel_chat_bp.route("/panel_cliente")
def panel_cliente():
    if "user" not in session:
        return redirect(url_for("google_login.login"))

    # Variables adicionales para estadísticas y configuración
    nombre_nora = "aura"  # Ejemplo, reemplazar con lógica dinámica si es necesario
    nombre_visible = "Nora AI"  # Ejemplo, reemplazar con lógica dinámica si es necesario
    modulos = ["contactos", "respuestas", "ia", "envios"]  # Ejemplo, reemplazar con datos reales
    total_contactos = 120  # Ejemplo, reemplazar con consulta real
    sin_ia = 30  # Ejemplo, reemplazar con consulta real
    sin_etiquetas = 50  # Ejemplo, reemplazar con consulta real
    total_respuestas = 15  # Ejemplo, reemplazar con consulta real

    return render_template(
        "panel_cliente.html",
        user=session["user"],
        nombre_nora=nombre_nora,
        nombre_visible=nombre_visible,
        modulos=modulos,
        total_contactos=total_contactos,
        sin_ia=sin_ia,
        sin_etiquetas=sin_etiquetas,
        total_respuestas=total_respuestas
    )
