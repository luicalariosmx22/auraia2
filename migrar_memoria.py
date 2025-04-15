import os
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

MEMORIA_PATH = "clientes/aura/database/memoria.json"

def cargar_memoria():
    if not os.path.exists(MEMORIA_PATH):
        print("⚠️ No existe el archivo memoria.json")
        return []

    with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    registros = []
    for telefono, recuerdos in data.items():
        for clave, valor in recuerdos.items():
            registros.append({
                "telefono": telefono,
                "clave": clave,
                "valor": str(valor),
                "fecha": datetime.utcnow().isoformat()
            })
    return registros

def insertar_en_supabase(datos):
    if not datos:
        print("⚠️ No hay memoria para insertar")
        return
    try:
        for r in datos:
            supabase.table("memoria").insert(r).execute()
        print(f"✅ {len(datos)} recuerdos insertados")
    except Exception as e:
        print(f"❌ Error al insertar memoria: {e}")

if __name__ == "__main__":
    registros = cargar_memoria()
    insertar_en_supabase(registros)
