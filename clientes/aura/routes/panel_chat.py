print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.utils.normalizador import normalizar_numero
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

panel_chat_bp = Blueprint("panel_chat", __name__)

def leer_contactos():
    """
    Carga la lista de contactos desde Supabase.
    """
    print("🔍 Iniciando función leer_contactos...")
    try:
        print("🔍 Leyendo contactos desde la tabla 'contactos'...")
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print("⚠️ No se encontraron contactos en la tabla 'contactos'.")
            return []

        contactos = []
        for contacto in response.data:
            if not contacto.get("nombre"):
                contacto["nombre"] = f"Usuario {contacto['telefono'][-10:]}"
            contactos.append(contacto)

        print(f"✅ Contactos cargados: {len(contactos)} contactos.")
        return contactos
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return []

def leer_historial(telefono):
    """
    Carga el historial de conversaciones de un contacto desde Supabase.
    """
    print(f"🔍 Iniciando función leer_historial para el teléfono: {telefono}")
    telefono = normalizar_numero(telefono)

    try:
        print(f"🔍 Buscando historial para el número exacto: {telefono}")
        response = (
            supabase
            .table("historial_conversaciones")
            .select("*")
            .eq("telefono", telefono)  # ← Comparación exacta
            .order("hora", desc=False)
            .execute()
        )
        if not response.data:
            print(f"⚠️ No se encontró historial para {telefono}.")
            return []

        for mensaje in response.data:
            if isinstance(mensaje.get("hora"), datetime.datetime):
                mensaje["hora"] = mensaje["hora"].strftime("%Y-%m-%d %H:%M:%S")

        print(f"✅ Historial cargado: {len(response.data)} registros.")
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar historial para {telefono}: {str(e)}")
        return []

def guardar_historial(nombre_nora, telefono, mensajes):
    """
    Guarda un conjunto de mensajes en la tabla 'historial_conversaciones'.
    """
    print(f"🔍 Iniciando función guardar_historial para el teléfono: {telefono}")
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": telefono,
            "mensaje": mensaje.get("texto") or mensaje.get("mensaje"),
            "emisor": mensaje["emisor"],
            "hora": mensaje.get("hora", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "timestamp": datetime.datetime.now().isoformat()
        }
        for mensaje in mensajes
    ]
    try:
        print(f"🔍 Guardando {len(registros)} registros en la tabla 'historial_conversaciones'...")
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if not response.data:
            print("❌ Error al guardar historial.")
        else:
            print("✅ Historial guardado correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

def generar_resumen_ia(mensajes):
    """
    Genera un resumen de los últimos mensajes utilizando OpenAI.
    """
    print("🔍 Iniciando función generar_resumen_ia...")
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
    """
    Renderiza el panel de chat para una Nora específica.
    """
    print(f"🔍 Iniciando función panel_chat para Nora: {nombre_nora}")
    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()
    lista = []
    for c in contactos:
        mensajes = leer_historial(c["telefono"])
        for mensaje in mensajes:
            if "fecha" in mensaje and isinstance(mensaje["fecha"], datetime.datetime):
                mensaje["fecha"] = mensaje["fecha"].strftime('%d-%b')
        lista.append({**c, "mensajes": mensajes})

    print(f"✅ Panel de chat renderizado para {len(contactos)} contactos.")
    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    """
    Proporciona el historial de chat de un contacto específico en formato JSON.
    """
    print(f"🔍 Iniciando función api_chat para el teléfono: {telefono}")
    try:
        telefono = normalizar_numero(telefono)
        print(f"🔍 Teléfono normalizado: {telefono}")

        contactos = leer_contactos()
        print(f"✅ Contactos cargados: {len(contactos)}")

        contacto = next((c for c in contactos if normalizar_numero(c["telefono"]) == telefono), {})
        print(f"🔍 Contacto encontrado: {contacto}")

        historial = leer_historial(telefono)
        print(f"✅ Historial cargado: {len(historial)} mensajes")

        if not contacto.get("nombre"):
            contacto["nombre"] = f"Usuario {telefono[-10:]}"

        for mensaje in historial:
            mensaje["remitente"] = "Tú" if mensaje["emisor"] == "nora" else contacto["nombre"]

        print(f"✅ Respuesta lista para el teléfono: {telefono}")
        return jsonify({
            "success": True,
            "contacto": contacto,
            "mensajes": historial
        })
    except Exception as e:
        print(f"❌ Error en api_chat para el teléfono {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    """
    Permite enviar un mensaje a un contacto y guardar el mensaje en el historial.
    """
    print("🔍 Iniciando función api_enviar_mensaje...")
    data = request.json
    print(f"🔍 Datos recibidos: {data}")
    telefono = normalizar_numero(data.get("numero"))
    texto = data.get("mensaje")

    if not all([telefono, texto]):
        print("❌ Datos incompletos para enviar mensaje.")
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    historial = leer_historial(telefono)
    historial.append({
        "emisor": "usuario",
        "mensaje": texto,
        "fecha": datetime.datetime.now().strftime("%d-%b %H:%M")
    })

    guardar_historial("Nora", telefono, historial)
    print(f"✅ Mensaje enviado y guardado en el historial para {telefono}.")
    return jsonify({"success": True})

@panel_chat_bp.route("/api/toggle-ia/<telefono>", methods=["POST"])
def api_toggle_ia(telefono):
    """
    Activa o desactiva la IA para un contacto específico.
    """
    print(f"🔍 Iniciando función api_toggle_ia para el teléfono: {telefono}")
    telefono = normalizar_numero(telefono)
    try:
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
    """
    Permite programar el envío de un mensaje a un contacto.
    """
    print("🔍 Iniciando función api_programar_envio...")
    data = request.json
    print(f"🔍 Datos recibidos: {data}")
    try:
        response = supabase.table("envios_programados").insert({
            "numero": data.get("numero"),
            "mensaje": data.get("mensaje"),
            "fecha": data.get("fecha"),
            "hora": data.get("hora")
        }).execute()
        if not response.data:
            print("❌ Error al programar envío.")
            return jsonify({"success": False})
        print(f"✅ Envío programado correctamente: {response.data}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al programar envío: {str(e)}")
        return jsonify({"success": False})