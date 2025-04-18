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

def leer_historial(telefono):
    try:
        # Eliminamos el filtro por "nombre_nora" ya que no existe en la tabla
        response = supabase.table("historial_conversaciones").select("*").eq("telefono", telefono).order("hora", ascending=True).execute()
        if not response.data:
            print(f"⚠️ No se encontró historial para {telefono}.")
            return []
        print(f"✅ Historial cargado para {telefono}: {response.data}")
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar historial: {str(e)}")
        return []

def guardar_historial(telefono, mensajes):
    registros = [
        {
            "telefono": telefono,
            "mensaje": mensaje["texto"],
            "emisor": mensaje["origen"],  # Cambiado de "origen" a "emisor" para coincidir con la tabla
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

@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()
    lista = []
    for c in contactos:
        mensajes = leer_historial(c["telefono"])
        lista.append({**c, "mensajes": mensajes})
    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    contactos = leer_contactos()
    contacto = next((c for c in contactos if c["telefono"] == telefono), {})
    historial = leer_historial(telefono)
    resumen = generar_resumen_ia(historial)
    print(f"✅ API Chat - Historial para {telefono}: {historial}")
    return jsonify({
        "success": True,
        "contacto": contacto,
        "mensajes": historial,
        "resumen_ia": resumen
    })

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    data = request.json
    telefono = data.get("numero")
    texto = data.get("mensaje")

    if not all([telefono, texto]):
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    historial = leer_historial(telefono)
    historial.append({
        "origen": "usuario",
        "texto": texto,
        "hora": datetime.datetime.now().strftime("%H:%M")
    })

    contactos = leer_contactos()
    contacto = next((c for c in contactos if c["telefono"] == telefono), {})
    if contacto.get("ia_activada"):
        respuesta = f"Respuesta IA a: {texto}"
        historial.append({
            "origen": "bot",
            "texto": respuesta,
            "hora": datetime.datetime.now().strftime("%H:%M")
        })

    guardar_historial(telefono, historial)
    return jsonify({"success": True})

@panel_chat_bp.route("/api/toggle-ia/<telefono>", methods=["POST"])
def api_toggle_ia(telefono):
    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Error al cargar contacto: {not response.data}")
            return jsonify({"success": False})

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)

        supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", telefono).execute()
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
            "hora": data.get("hora")
        }).execute()
        if not response.data:
            print(f"❌ Error al programar envío: {not response.data}")
            return jsonify({"success": False})
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al programar envío: {str(e)}")
        return jsonify({"success": False})

function cargarChat(telefono) {
    fetch(`/api/chat/${telefono}`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos del chat:", data); // Verifica los datos en la consola
            if (data.success) {
                mostrarMensajes(data.mensajes);
            } else {
                console.error("Error al cargar el chat:", data.error);
            }
        })
        .catch(error => console.error("Error al cargar el chat:", error));
}