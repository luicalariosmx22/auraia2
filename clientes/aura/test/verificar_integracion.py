import os
from supabase import create_client
from dotenv import load_dotenv

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_tabla(tabla, descripcion):
    """
    Verifica si una tabla en Supabase tiene datos.
    """
    try:
        response = supabase.table(tabla).select("*").limit(1).execute()
        if not response.data:
            print(f"❌ FALTA: {descripcion} → Tabla '{tabla}' vacía o no encontrada.")
            return False
        print(f"✅ OK: {descripcion} → Tabla '{tabla}' contiene datos.")
        return True
    except Exception as e:
        print(f"❌ Error al verificar tabla '{tabla}': {e}")
        return False

def revisar_bot_data():
    """
    Verifica la tabla `bot_data` en Supabase.
    """
    if not check_tabla("bot_data", "Respuestas automáticas (bot_data)"):
        return

    try:
        response = supabase.table("bot_data").select("*").execute()
        data = response.data

        if any("hola" in item.get("palabras_clave", []) for item in data):
            print("✅ Palabra clave 'hola' encontrada en bot_data.")
        else:
            print("⚠️ No se encontró 'hola' como palabra clave. Nora no podrá saludar.")
    except Exception as e:
        print(f"❌ Error al verificar bot_data: {e}")

def revisar_conocimiento():
    """
    Verifica la tabla `conocimiento` en Supabase.
    """
    if not check_tabla("conocimiento", "Archivo de conocimiento para IA"):
        return

    try:
        response = supabase.table("conocimiento").select("*").execute()
        contenido = response.data

        if len(contenido) < 1:
            print("⚠️ Tabla de conocimiento cargada pero está vacía.")
        else:
            print("✅ Contenido de conocimiento cargado correctamente.")
    except Exception as e:
        print(f"❌ Error al verificar conocimiento: {e}")

def revisar_settings():
    """
    Verifica la tabla `settings` en Supabase.
    """
    if not check_tabla("settings", "Configuración de Nora (settings)"):
        return

    try:
        response = supabase.table("settings").select("*").execute()
        settings = response.data[0] if response.data else {}

        for clave in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
            estado = settings.get(clave, False)
            print(f"{'✅' if estado else '⚠️'} {clave} → {estado}")
    except Exception as e:
        print(f"❌ Error al verificar settings: {e}")

if __name__ == "__main__":
    print("🔍 Verificando configuración de Nora...\n")
    revisar_bot_data()
    print()
    revisar_conocimiento()
    print()
    revisar_settings()
