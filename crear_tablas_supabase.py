import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cargar_contactos_con_etiquetas():
    ruta = "clientes/aura/database/contactos.json"
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar {ruta}: {e}")
        return []

def insertar_etiquetas(contactos):
    registros = []
    for c in contactos:
        telefono = c.get("numero")
        etiquetas = c.get("etiquetas", [])
        for etiqueta in etiquetas:
            registros.append({
                "telefono": telefono,
                "etiqueta": etiqueta
            })
    
    if registros:
        try:
            for r in registros:
                supabase.table("etiquetas_contacto").insert(r).execute()
            print(f"✅ {len(registros)} etiquetas insertadas en Supabase")
        except Exception as e:
            print(f"❌ Error al insertar etiquetas: {e}")
    else:
        print("⚠️ No hay etiquetas para insertar")

# Ejecutar
contactos = cargar_contactos_con_etiquetas()
insertar_etiquetas(contactos)
