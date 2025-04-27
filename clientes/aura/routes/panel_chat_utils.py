print("✅ panel_chat_utils.py cargado correctamente")

from dotenv import load_dotenv
import os
import datetime
from supabase import create_client
from dateutil import parser

# Cargar configuración
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Funciones utilitarias para panel de chat

def normalizar_numero(numero):
    print(f"🔵 Normalizando número: {numero}")
    numero = str(numero)
    numero = ''.join(filter(str.isdigit, numero))
    if len(numero) == 10:
        return f"521{numero}"
    if len(numero) == 12 and numero.startswith("52"):
        return f"5{numero}"
    return numero

def parse_fecha(fecha_str):
    print(f"🔵 Parseando fecha: {fecha_str}")
    try:
        return parser.parse(fecha_str)
    except Exception as e:
        print(f"⚠️ Error al parsear fecha: {e}")
        return datetime.datetime.min

def leer_contactos(nombre_nora=None):  # 👈 Added optional parameter
    print(f"🔵 Iniciando lectura de contactos desde 'contactos'... nombre_nora={nombre_nora}")
    try:
        query = supabase.table("contactos").select("*")
        if nombre_nora:
            query = query.eq("nombre_nora", nombre_nora)  # 👈 Filter by nombre_nora if provided
        response = query.execute()
        print(f"✅ Contactos leídos: {len(response.data) if response.data else 0}")
        return response.data or []
    except Exception as e:
        print(f"❌ Error leyendo contactos: {str(e)}")
        return []

def leer_historial(telefono):
    print(f"🔵 Iniciando lectura de historial para: {telefono}")
    try:
        response = (
            supabase
            .table("historial_conversaciones")
            .select("*")
            .eq("telefono", telefono)
            .order("hora", desc=True)
            .limit(20)
            .execute()
        )
        print(f"✅ Historial leído: {len(response.data) if response.data else 0}")
        return response.data or []
    except Exception as e:
        print(f"❌ Error leyendo historial: {str(e)}")
        return []

def guardar_historial(nombre_nora, telefono, mensajes):
    print(f"🔵 Guardando historial para: {telefono}")
    registros = []
    for mensaje in mensajes:
        registros.append({
            "nombre_nora": nombre_nora,
            "telefono": telefono,
            "mensaje": mensaje.get("mensaje"),
            "emisor": mensaje.get("emisor"),
            "hora": mensaje.get("hora") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.datetime.now().isoformat()
        })
    try:
        supabase.table("historial_conversaciones").insert(registros).execute()
        print(f"✅ Historial guardado correctamente: {len(registros)} mensajes")
    except Exception as e:
        print(f"❌ Error guardando historial: {str(e)}")
