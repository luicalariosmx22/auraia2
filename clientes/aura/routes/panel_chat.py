print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.utils.normalizador import normalizar_numero  # ✅ IMPORTADO
import os
import datetime
import openai

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL o SUPABASE_KEY no están configurados.")
else:
    print("✅ Conexión con Supabase configurada correctamente.")

openai.api_key = os.getenv("OPENAI_API_KEY")

panel_chat_bp = Blueprint("panel_chat_aura", __name__)

def leer_contactos():
    try:
        print("🔍 Leyendo contactos desde la tabla 'contactos'...")
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print(f"⚠️ No se encontraron contactos en la tabla 'contactos'.")
            return []
        print(f"✅ Contactos cargados: {response.data}")
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return []

def leer_historial(telefono):
    telefono = normalizar_numero(telefono)
    numero_simplificado = telefono[-10:]  # Extraer los últimos 10 dígitos para simplificar la búsqueda

    try:
        print(f"🔍 Buscando historial para número simplificado: {numero_simplificado}")
        response = (
            supabase
            .table("historial_conversaciones")
            .select("*")
            .like("telefono", f"%{numero_simplificado}")  # 🧠 Busca coincidencia parcial
            .order("hora", desc=False)
            .execute()
        )
        if not response.data:
            print(f"⚠️ No se encontró historial para {telefono}.")
            return []
        print(f"✅ Historial cargado: {len(response.data)} registros.")
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar historial para {telefono}: {str(e)}")
        return []

def guardar_historial(nombre_nora, telefono, mensajes):
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": telefono,
            "mensaje": mensaje.get("texto") or mensaje.get("mensaje"),
            "emisor": mensaje["emisor"],
            "hora": mensaje["hora"],
            "timestamp": datetime.datetime.now()
        }
        for mensaje in mensajes
    ]
    try:
        print(f"🔍 Guardando historial en la tabla 'historial_conversaciones': {registros}")
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if not response.data:
            print(f"❌ Error al guardar historial: {not response.data}")
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

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
        print("🔍 Generando resumen con IA...")
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        resumen = respuesta.choices[0].message.content.strip()
        print(f"✅ Resumen generado: {resumen}")
        return resumen
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
        # Asegúrate de que cada mensaje tenga un atributo 'fecha' correctamente formateado
        for mensaje in mensajes:
            if "fecha" in mensaje and isinstance(mensaje["fecha"], datetime.datetime):
                mensaje["fecha"] = mensaje["fecha"].strftime('%d-%b')  # Formato: 18-Abr
        lista.append({**c, "mensajes": mensajes})

    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    telefono = normalizar_numero(telefono)
    print(f"🔍 API Chat - Cargando datos para el teléfono: {telefono}...")
    contactos = leer_contactos()
    contacto = next((c for c in contactos if normalizar_numero(c["telefono"]) == telefono), {})
    historial = leer_historial(telefono)  # Función que obtiene los mensajes del contacto

    # Asegúrate de que cada mensaje tenga un timestamp formateado
    for mensaje in historial:
        if "fecha" in mensaje and isinstance(mensaje["fecha"], datetime):
            mensaje["fecha"] = mensaje["fecha"].strftime('%d-%b %H:%M')  # Formato: 18-Abr 14:30

    resumen = generar_resumen_ia(historial)  # Opcional: Generar un resumen con IA
    print(f"✅ API Chat - Datos cargados para {telefono}: {historial}")
    return jsonify({
        "success": True,
        "contacto": contacto,
        "mensajes": historial,
        "resumen_ia": resumen
    })

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    data = request.json
    print(f"🔍 API Enviar Mensaje - Datos recibidos: {data}")
    telefono = normalizar_numero(data.get("numero"))
    texto = data.get("mensaje")

    if not all([telefono, texto]):
        print("❌ Datos incompletos para enviar mensaje.")
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    historial = leer_historial(telefono)
    historial.append({
        "emisor": "usuario",
        "texto": texto,
        "hora": datetime.datetime.now().strftime("%H:%M")
    })

    contactos = leer_contactos()
    contacto = next((c for c in contactos if normalizar_numero(c["telefono"]) == telefono), {})
    print(f"✅ Contacto encontrado: {contacto}")

    if contacto.get("ia_activada"):
        respuesta = f"Respuesta IA a: {texto}"
        historial.append({
            "emisor": "bot",
            "texto": respuesta,
            "hora": datetime.datetime.now().strftime("%H:%M")
        })
        print(f"🤖 Respuesta generada por IA: {respuesta}")

    nombre_nora = contacto.get("nombre_nora", "Nora")
    print(f"🔍 Guardando historial para {telefono} con nombre_nora: {nombre_nora}")
    guardar_historial(nombre_nora, telefono, historial)

    return jsonify({"success": True})

@panel_chat_bp.route("/api/toggle-ia/<telefono>", methods=["POST"])
def api_toggle_ia(telefono):
    telefono = normalizar_numero(telefono)
    try:
        print(f"🔍 API Toggle IA - Cambiando estado de IA para {telefono}...")
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Error al cargar contacto para {telefono}.")
            return jsonify({"success": False})

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)
        supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", telefono).execute()
        print(f"✅ Estado de IA cambiado para {telefono}: {nuevo_estado}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA para {telefono}: {str(e)}")
        return jsonify({"success": False})

@panel_chat_bp.route("/api/programar-envio", methods=["POST"])
def api_programar_envio():
    data = request.json
    print(f"🔍 API Programar Envío - Datos recibidos: {data}")
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
        print(f"✅ Envío programado: {response.data}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al programar envío: {str(e)}")
        return jsonify({"success": False})
