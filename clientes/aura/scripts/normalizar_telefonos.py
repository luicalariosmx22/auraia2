# clientes/aura/scripts/normalizar_telefonos.py

from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar_numero(n):
    """Quita todo excepto los últimos 10 dígitos y agrega +521"""
    digitos = ''.join(filter(str.isdigit, n))
    return f"+521{digitos[-10:]}" if len(digitos) >= 10 else n

def actualizar_tabla_historial():
    print("\n📦 Corrigiendo tabla: historial_conversaciones")
    response = supabase.table("historial_conversaciones").select("id, telefono").execute()
    for r in response.data:
        original = r["telefono"]
        nuevo = normalizar_numero(original)
        if original != nuevo:
            print(f"🔄 {original} → {nuevo}")
            supabase.table("historial_conversaciones").update({"telefono": nuevo}).eq("id", r["id"]).execute()

def actualizar_tabla_contactos():
    print("\n📦 Corrigiendo tabla: contactos")
    response = supabase.table("contactos").select("id, telefono").execute()
    for r in response.data:
        original = r["telefono"]
        nuevo = normalizar_numero(original)
        if original != nuevo:
            print(f"🔄 {original} → {nuevo}")
            supabase.table("contactos").update({"telefono": nuevo}).eq("id", r["id"]).execute()

if __name__ == "__main__":
    actualizar_tabla_historial()
    actualizar_tabla_contactos()
    print("\n✅ Todos los teléfonos fueron normalizados correctamente.")
