print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os
import datetime
import openai

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

openai.api_key = os.getenv("OPENAI_API_KEY")

panel_chat_bp = Blueprint("panel_chat_aura", __name__)

def leer_contactos():
    try:
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar contactos: {not response.data}")
            return []
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return []

def leer_historial(nombre_nora, numero):
    try:
        response = supabase.table("historial_conversaciones").select("*").eq("nombre_nora", nombre_nora).eq("telefono", numero).execute()
        if not response.data:
            print(f"❌ Error al cargar historial: {not response.data}")
            return []
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar historial: {str(e)}")
        return []

def guardar_historial(nombre_nora, numero, mensajes):
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": numero,
            "mensaje": mensaje["texto"],
            "origen": mensaje["origen"],
            "hora": mensaje["hora"]
        }
        for mensaje in mensajes
    ]
    try:
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if not response.data:
            print(f"❌ Error al guardar historial: {not response.data}")
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

def generar_resumen_ia(mensajes):
    if not mensajes:
        return "No hay suficientes mensajes para generar un resumen."

    texto = "\n".join([f"{m['origen']}: {m['mensaje']}" for m in mensajes[-20:]])

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

@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()
    lista = []
    for c in contactos:
        mensajes = leer_historial(nombre_nora, c["numero"])
        lista.append({**c, "mensajes": mensajes})
    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

@panel_chat_bp.route("/api/chat/<numero>")
def api_chat(numero):
    contactos = leer_contactos()
    contacto = next((c for c in contactos if c["numero"] == numero), {})
    historial = leer_historial("aura", numero)
    resumen = generar_resumen_ia(historial)
    return jsonify({
        "success": True,
        "contacto": contacto,
        "mensajes": historial,
        "resumen_ia": resumen
    })

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    data = request.json
    numero = data.get("numero")
    texto = data.get("mensaje")
    nombre_nora = data.get("nombre_nora")

    if not all([numero, texto, nombre_nora]):
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    historial = leer_historial(nombre_nora, numero)
    historial.append({
        "origen": "usuario",
        "mensaje": texto,
        "hora": datetime.datetime.now().strftime("%H:%M")
    })

    contactos = leer_contactos()
    contacto = next((c for c in contactos if c["numero"] == numero), {})
    if contacto.get("ia_activada"):
        respuesta = f"Respuesta IA a: {texto}"
        historial.append({
            "origen": "nora",
            "mensaje": respuesta,
            "hora": datetime.datetime.now().strftime("%H:%M")
        })

    guardar_historial(nombre_nora, numero, historial)
    return jsonify({"success": True})

@panel_chat_bp.route("/api/toggle-ia/<numero>", methods=["POST"])
def api_toggle_ia(numero):
    try:
        response = supabase.table("contactos").select("*").eq("numero", numero).execute()
        if not response.data:
            print(f"❌ Error al cargar contacto: {not response.data}")
            return jsonify({"success": False})

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)

        supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("numero", numero).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA: {str(e)}")
        return jsonify({"success": False})

@panel_chat_bp.route("/api/programar-envio", methods=["POST"])
def api_programar_envio():
    data = request.json
    try:
        response = supabase.table("envios_programados").insert({
            "numero": data.get("numero"),
            "mensaje": data.get("mensaje"),
            "fecha": data.get("fecha"),
            "hora": data.get("hora"),
            "nombre_nora": data.get("nombre_nora")
        }).execute()
        if not response.data:
            print(f"❌ Error al programar envío: {not response.data}")
            return jsonify({"success": False})
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al programar envío: {str(e)}")
        return jsonify({"success": False})