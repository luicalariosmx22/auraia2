import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

BASE = "clientes/aura/database"

# Definición centralizada
mapeo_archivos = {
    "contactos.json": "contactos",
    "bot_data.json": "bot_data",
    "config.json": "configuracion_bot",
    "settings.json": "configuracion_bot",
    "categorias.json": "categorias",
    "etiquetas.json": "etiquetas",
    "contactos_info.json": "contactos_info",
    "logs_errores.json": "logs_errores",
    "historial_conversaciones.json": "historial_conversaciones",
    "envios/envios_programados.json": "envios_programados"
}

def insertar(tabla, datos):
    if not datos:
        print(f"⚠️ No hay datos para '{tabla}'")
        return
    try:
        for d in datos:
            supabase.table(tabla).insert(d).execute()
        print(f"✅ {len(datos)} registros insertados en '{tabla}'")
    except Exception as e:
        print(f"❌ Error en '{tabla}': {e}")

def normalizar_contactos(data):
    return [
        {
            "nombre": c.get("nombre"),
            "telefono": c.get("numero"),
            "ia_activada": c.get("ia_activada", True)
        } for c in data
    ]

def insertar_etiquetas_contacto(data):
    etiquetas = []
    for c in data:
        numero = c.get("numero")
        for etiqueta in c.get("etiquetas", []):
            etiquetas.append({
                "telefono": numero,
                "etiqueta": etiqueta
            })
    insertar("etiquetas_contacto", etiquetas)

def cargar_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"❌ Error abriendo {path}: {e}")
        return []

def migrar():
    # Migrar contactos + etiquetas_contacto
    contactos_data = cargar_json(f"{BASE}/contactos.json")
    insertar("contactos", normalizar_contactos(contactos_data))
    insertar_etiquetas_contacto(contactos_data)

    for archivo, tabla in mapeo_archivos.items():
        if archivo == "contactos.json":
            continue  # Ya migrado
        path = os.path.join(BASE, archivo)
        datos = cargar_json(path)
        insertar(tabla, datos)

if __name__ == "__main__":
    migrar()
