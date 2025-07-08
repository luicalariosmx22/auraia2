from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalizar_telefono(n):
    """Devuelve +521XXXXXXXXXX"""
    digitos = ''.join(filter(str.isdigit, n))
    return f"+521{digitos[-10:]}" if len(digitos) >= 10 else n

def normalizar_nombre_nora(nombre):
    """Estándar: aura (en minúsculas)"""
    if not nombre or nombre.strip().lower() != "aura":
        return "aura"
    return nombre.strip().lower()

def actualizar_tabla(tabla, campos):
    print(f"\n📦 Corrigiendo tabla: {tabla}")
    response = supabase.table(tabla).select(",".join(["id"] + campos)).execute()
    total = 0

    for r in response.data:
        updates = {}
        if "telefono" in campos:
            tel_original = r.get("telefono", "")
            tel_nuevo = normalizar_telefono(tel_original)
            if tel_original != tel_nuevo:
                updates["telefono"] = tel_nuevo

        if "nombre_nora" in campos:
            nombre_original = r.get("nombre_nora", "")
            nombre_nuevo = normalizar_nombre_nora(nombre_original)
            if nombre_original != nombre_nuevo:
                updates["nombre_nora"] = nombre_nuevo

        if updates:
            print(f"🔄 {tabla} ID {r['id']} → {updates}")
            supabase.table(tabla).update(updates).eq("id", r["id"]).execute()
            total += 1

    print(f"✅ {total} registros actualizados en {tabla}.")

if __name__ == "__main__":
    actualizar_tabla("historial_conversaciones", ["telefono", "nombre_nora"])
    actualizar_tabla("contactos", ["telefono"])  # ← solo teléfono
    print("\n✅ Todos los números y nombre_nora fueron normalizados correctamente.")
