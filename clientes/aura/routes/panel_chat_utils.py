print("✅ panel_chat_utils.py cargado correctamente")

import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.routes.panel_chat_helpers import parse_fecha
from supabase import create_client
from dotenv import load_dotenv
import os
import openai
from dateutil import parser

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY")


def leer_contactos():
    print("🔍 Iniciando función leer_contactos...")
    try:
        print("🔍 Consultando tabla 'contactos' en Supabase...")
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print("⚠️ No se encontraron contactos en la tabla 'contactos'.")
            return []

        print("🔍 Procesando contactos obtenidos...")
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
    print(f"🔍 Iniciando función leer_historial para el teléfono: {telefono}")
    telefono = normalizar_numero(telefono)
    print(f"🔍 Teléfono normalizado: {telefono}")

    try:
        print("🔍 Consultando tabla 'historial_conversaciones' en Supabase...")
        response = (
            supabase
            .table("historial_conversaciones")
            .select("*")
            .eq("telefono", telefono)
            .order("hora", desc=False)
            .execute()
        )
        if not response.data:
            print(f"⚠️ No se encontró historial para {telefono}.")
            return []

        print("🔍 Procesando mensajes del historial...")
        for mensaje in response.data:
            try:
                mensaje["hora"] = parser.parse(mensaje["hora"])
                print(f"✅ Fecha parseada: {mensaje['hora']}")
            except Exception as e:
                print(f"⚠️ No se pudo parsear la fecha del mensaje: {mensaje.get('hora')} → {e}")
                mensaje["hora"] = datetime.datetime.min

        print(f"✅ Historial cargado: {len(response.data)} registros.")
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar historial para {telefono}: {str(e)}")
        return []


def guardar_historial(nombre_nora, telefono, mensajes):
    print(f"🔍 Iniciando función guardar_historial para el teléfono: {telefono}")
    print(f"🔍 Preparando registros para guardar...")
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
    print(f"🔍 Registros preparados: {len(registros)}")

    try:
        print("🔍 Insertando registros en la tabla 'historial_conversaciones'...")
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if not response.data:
            print("❌ Error al guardar historial.")
        else:
            print("✅ Historial guardado correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")


def generar_resumen_ia(mensajes):
    print("🔍 Iniciando función generar_resumen_ia...")
    if not mensajes:
        print("⚠️ No hay suficientes mensajes para generar un resumen.")
        return "No hay suficientes mensajes para generar un resumen."

    print("🔍 Preparando texto para el resumen...")
    texto = "\n".join([f"{m['emisor']}: {m['mensaje']}" for m in mensajes[-20:]])
    prompt = f"""
Eres un asistente profesional. Resume brevemente esta conversación entre un cliente y una IA llamada Nora. El resumen debe identificar si el cliente está interesado en algo, si ya fue atendido, y si hay seguimiento pendiente:

{texto}

Resumen:
"""
    print("🔍 Enviando solicitud a OpenAI...")
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        resumen = respuesta.choices[0].message.content.strip()
        print(f"✅ Resumen generado: {resumen}")
        return resumen
    except Exception as e:
        print(f"❌ Error al generar resumen con IA: {e}")
        return "No se pudo generar el resumen con IA."


def obtener_fecha_mas_reciente(mensajes):
    print("🔍 Iniciando función obtener_fecha_mas_reciente...")
    if not mensajes:
        print("⚠️ No hay mensajes para procesar.")
        return ""
    try:
        print("🔍 Calculando la fecha más reciente...")
        fecha_mas_reciente = max(m["hora"] for m in mensajes if "hora" in m and m["hora"])
        print(f"✅ Fecha más reciente: {fecha_mas_reciente}")
        return fecha_mas_reciente
    except Exception as e:
        print(f"❌ Error al obtener la fecha más reciente: {str(e)}")
        return ""
