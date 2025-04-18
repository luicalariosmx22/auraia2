import os
import json
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

# Configurar Supabase
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

HISTORIAL_PATH = "clientes/aura/database/historial"

def cargar_archivos_historial():
    """
    Cargar los archivos JSON del historial desde la carpeta local.
    """
    archivos = []
    if not os.path.exists(HISTORIAL_PATH):
        print(f"❌ No se encontró la carpeta {HISTORIAL_PATH}")
        return archivos

    for archivo in os.listdir(HISTORIAL_PATH):
        if archivo.endswith(".json"):
            ruta = os.path.join(HISTORIAL_PATH, archivo)
            telefono = archivo.replace(".json", "")
            archivos.append((telefono, ruta))

    return archivos

def cargar_json(ruta):
    """
    Leer un archivo JSON y devolver su contenido.
    """
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error al leer {ruta}: {e}")
        return []

def preparar_registros(telefono, mensajes):
    """
    Preparar los registros para insertarlos en Supabase.
    """
    registros = []
    for mensaje in mensajes:
        registros.append({
            "telefono": telefono,
            "mensaje": mensaje.get("mensaje", ""),
            "tipo": mensaje.get("tipo", "desconocido"),
            "fecha": mensaje.get("fecha", datetime.now().isoformat())
        })
    return registros

def insertar_en_supabase(registros):
    """
    Insertar los registros en la tabla historial_conversaciones en Supabase.
    """
    try:
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if response.error:
            print(f"❌ Error al insertar registros en Supabase: {response.error}")
        else:
            print(f"✅ {len(registros)} registros insertados correctamente en Supabase")
    except Exception as e:
        print(f"❌ Error al insertar registros en Supabase: {e}")

def migrar_historial():
    """
    Migrar los archivos JSON del historial a Supabase.
    """
    archivos = cargar_archivos_historial()
    if not archivos:
        print("❌ No se encontraron archivos de historial para migrar.")
        return

    for telefono, ruta in archivos:
        print(f"📂 Procesando historial para {telefono} desde {ruta}")
        mensajes = cargar_json(ruta)
        if not mensajes:
            print(f"⚠️ No se encontraron mensajes en {ruta}")
            continue

        registros = preparar_registros(telefono, mensajes)
        insertar_en_supabase(registros)

    print("✅ Migración completada.")

if __name__ == "__main__":
    migrar_historial()
