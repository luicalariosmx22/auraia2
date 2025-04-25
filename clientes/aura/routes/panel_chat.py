print("✅ panel_chat.py cargado correctamente")

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.utils.normalizador import normalizar_numero
import os
import datetime
from dateutil import parser
import openai
from dateutil import parser

def parse_fecha(fecha_str):
    """
    Intenta analizar una fecha desde una cadena. Si falla, devuelve datetime.datetime.min.
    """
    try:
        return parser.parse(fecha_str)
    except Exception as e:
        print(f"⚠️ Error al analizar la fecha '{fecha_str}': {e}")
        return datetime.datetime.min

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
            try:
                mensaje["hora"] = parser.parse(mensaje["hora"])
            except Exception as e:
                print(f"⚠️ No se pudo parsear la fecha del mensaje: {mensaje.get('hora')} → {e}")
                mensaje["hora"] = datetime.datetime.min

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

def obtener_fecha_mas_reciente(mensajes):
    """
    Obtiene la fecha más reciente de los mensajes de un contacto.
    """
    if not mensajes:
        return ""
    try:
        return max(m["hora"] for m in mensajes if "hora" in m and m["hora"])
    except Exception as e:
        print(f"❌ Error al obtener la fecha más reciente: {str(e)}")
        return ""

@panel_chat_bp.route("/<nombre_nora>")
def panel_chat(nombre_nora):
    """
    Renderiza el panel de chat para una Nora específica.
    """
    print(f"🔍 Iniciando función panel_chat para Nora: {nombre_nora}")
    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()

    # Crear la lista de contactos con su ultimo_mensaje ya formateado
    lista = []
    for c in contactos:
        ultimo_mensaje_str = c.get("ultimo_mensaje")

        try:
            # Parseamos la fecha del último mensaje o asignamos una fecha mínima
            fecha_ultimo = datetime.datetime.strptime(ultimo_mensaje_str, "%Y-%m-%d %H:%M:%S") if ultimo_mensaje_str else datetime.datetime(1900, 1, 1)
        except Exception as e:
            print(f"❌ Error al parsear fecha en {c.get('telefono', 'desconocido')}: {e}")
            fecha_ultimo = datetime.datetime(1900, 1, 1)

        lista.append({
            **c,
            "fecha_ultimo_mensaje": fecha_ultimo,  # Agregamos la fecha parseada
        })

    # Ordenar contactos por la fecha más reciente en su historial de mensajes
    contactos_ordenados = sorted(
        lista,
        key=lambda c: obtener_fecha_mas_reciente(c.get("mensajes", [])),
        reverse=True
    )

    # Extraer etiquetas únicas
    etiquetas_unicas = set()
    for c in contactos_ordenados:
        etiquetas_unicas.update(c.get("etiquetas", []))

    print(f"✅ Panel de chat renderizado para {len(contactos)} contactos.")
    return render_template(
        "panel_chat.html",
        contactos=contactos_ordenados,  # ⬅️ Aquí
        nombre_nora=nombre_nora,
        etiquetas_unicas=sorted(etiquetas_unicas)
    )

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

@panel_chat_bp.route("/api/etiqueta/<telefono>", methods=["POST", "DELETE"])
def api_gestion_etiqueta(telefono):
    """
    Agrega o elimina etiquetas a un contacto.
    POST → Agrega
    DELETE → Elimina
    """
    print(f"🔍 Iniciando función api_gestion_etiqueta para el teléfono: {telefono}")
    body = request.get_json()
    etiqueta = body.get("etiqueta", "").strip().lower()
    telefono = normalizar_numero(telefono)

    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Contacto no encontrado para el teléfono: {telefono}")
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        etiquetas = set(contacto.get("etiquetas", []))

        if request.method == "POST":
            etiquetas.add(etiqueta)
            print(f"✅ Etiqueta '{etiqueta}' agregada al contacto {telefono}.")
        elif request.method == "DELETE":
            etiquetas.discard(etiqueta)
            print(f"✅ Etiqueta '{etiqueta}' eliminada del contacto {telefono}.")

        supabase.table("contactos").update({"etiquetas": list(etiquetas)}).eq("telefono", telefono).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error en api_gestion_etiqueta para el teléfono {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)})