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
        print("🔍 Intentando leer contactos desde Supabase...")
        response = supabase.table("contactos").select("*").execute()
        print(f"✅ Contactos cargados: {len(response.data)}")
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
        print(f"✅ Historial cargado: {len(response.data)} mensajes.")
        return response.data or []
    except Exception as e:
        print(f"❌ Error al cargar historial para {telefono}: {str(e)}")
        return []

def generar_resumen_ia(mensajes):
    if not mensajes:
        print("⚠️ No hay suficientes mensajes para generar un resumen.")
        return "No hay suficientes mensajes para generar un resumen."

    texto = "\n".join([f"{m['emisor']}: {m['mensaje']}" for m in mensajes[-20:]])
    prompt = f"""
Eres un asistente profesional. Resume brevemente esta conversación entre un cliente y una IA llamada Nora. El resumen debe identificar si el cliente está interesado en algo, si ya fue atendido, y si hay seguimiento pendiente:

{texto}

Resumen:
"""
    try:
        print("🔍 Generando resumen con OpenAI...")
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        print("✅ Resumen generado con éxito.")
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error al generar resumen con IA: {e}")
        return "No se pudo generar el resumen con IA."

# Ruta para el panel principal
@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    if not session.get("email"):
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("google_login.login"))

    try:
        print("🔍 Cargando contactos para el panel principal...")
        contactos = leer_contactos()
        lista = []
        for c in contactos:
            print(f"🔍 Leyendo historial para contacto: {c['telefono']}")
            mensajes = leer_historial(c["telefono"], limite=10)  # Solo últimos 10 mensajes
            lista.append({**c, "mensajes": mensajes})
        print("✅ Contactos y mensajes cargados con éxito.")
        return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)
    except Exception as e:
        print(f"❌ Error en la ruta /panel/chat/{nombre_nora}: {str(e)}")
        return "Error al cargar el panel", 500

# Ruta para obtener el historial de un contacto
@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    try:
        offset = int(request.args.get("offset", 0))  # 👈 ahora acepta offset por query param
        telefono = normalizar_numero(telefono)
        print(f"🔍 Cargando historial para el número: {telefono} con offset {offset}...")
        historial = leer_historial(telefono, limite=20, offset=offset)

        contacto = None
        print("🔍 Buscando información del contacto...")
        contactos = leer_contactos()
        for c in contactos:
            if normalizar_numero(c["telefono"])[-10:] == telefono[-10:]:
                contacto = c
                break

        resumen = generar_resumen_ia(historial)
        print("✅ Respuesta de la API generada con éxito.")
        return jsonify({
            "success": True,
            "contacto": contacto or {},
            "mensajes": historial,
            "resumen_ia": resumen
        })
    except Exception as e:
        print(f"❌ Error en la ruta /api/chat/{telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Ruta para el panel limitado (clientes)
@panel_chat_bp.route("/panel_cliente")
def panel_cliente():
    if not session.get("email"):
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("google_login.login"))

    try:
        print("🔍 Cargando datos para el panel cliente...")
        nombre_nora = "aura"  # Ejemplo, reemplazar con lógica dinámica si es necesario
        nombre_visible = "Nora AI"  # Ejemplo, reemplazar con lógica dinámica si es necesario
        modulos = ["contactos", "respuestas", "ia", "envios"]  # Ejemplo, reemplazar con datos reales
        total_contactos = 120  # Ejemplo, reemplazar con consulta real
        sin_ia = 30  # Ejemplo, reemplazar con consulta real
        sin_etiquetas = 50  # Ejemplo, reemplazar con consulta real
        total_respuestas = 15  # Ejemplo, reemplazar con consulta real

        print("✅ Datos cargados con éxito para el panel cliente.")
        return render_template(
            "panel_cliente.html",
            user={"name": session.get("name", "Usuario")},
            nombre_nora=nombre_nora,
            nombre_visible=nombre_visible,
            modulos=modulos,
            total_contactos=total_contactos,
            sin_ia=sin_ia,
            sin_etiquetas=sin_etiquetas,
            total_respuestas=total_respuestas
        )
    except Exception as e:
        print(f"❌ Error en la ruta /panel_cliente: {str(e)}")
        return "Error al cargar el panel cliente", 500

@panel_chat_bp.route("/api/etiqueta/<telefono>", methods=["POST", "DELETE"])
def api_gestion_etiqueta(telefono):
    """
    Ruta para agregar o eliminar etiquetas de un contacto.
    """
    try:
        body = request.get_json()
        etiqueta = body.get("etiqueta", "").strip().lower()
        telefono = normalizar_numero(telefono)

        # Buscar el contacto en la base de datos
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        etiquetas = set(contacto.get("etiquetas", []))

        # Agregar o eliminar la etiqueta según el método HTTP
        if request.method == "POST":
            etiquetas.add(etiqueta)
        elif request.method == "DELETE":
            etiquetas.discard(etiqueta)

        # Actualizar las etiquetas en la base de datos
        supabase.table("contactos").update({"etiquetas": list(etiquetas)}).eq("telefono", telefono).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error en la gestión de etiquetas para {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
