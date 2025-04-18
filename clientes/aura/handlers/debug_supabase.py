import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from termcolor import colored

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def mostrar_estado(texto, estado):
    if estado == "ok":
        print(f"{texto}: " + colored("🟢 OK", "green"))
    elif estado == "advertencia":
        print(f"{texto}: " + colored("🟡 Advertencia", "yellow"))
    else:
        print(f"{texto}: " + colored("🔴 ERROR", "red"))

def verificar_variables_entorno():
    errores = 0
    if not SUPABASE_URL:
        mostrar_estado("SUPABASE_URL", "error")
        errores += 1
    else:
        mostrar_estado("SUPABASE_URL", "ok")
    if not SUPABASE_KEY:
        mostrar_estado("SUPABASE_KEY", "error")
        errores += 1
    else:
        mostrar_estado("SUPABASE_KEY", "ok")
    return errores == 0

def conectar_supabase():
    try:
        client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        mostrar_estado(f"Conexión a Supabase fallida: {e}", "error")
        return None

def probar_tabla_contactos(client):
    try:
        test_contact = {
            "nombre": "Prueba Luis",
            "telefono": "0000000000",
            "etiquetas": ["test"],
            "creado_en": datetime.now().isoformat()
        }
        client.table("contactos").insert(test_contact).execute()
        mostrar_estado("Inserción en tabla 'contactos'", "ok")
    except Exception as e:
        mostrar_estado(f"Tabla 'contactos' no disponible o falló la inserción: {e}", "error")

def probar_tabla_mensajes(client):
    try:
        test_msg = {
            "numero": "0000000000",
            "mensaje_usuario": "Hola, esto es una prueba",
            "respuesta_bot": "Hola, soy Nora AI.",
            "creado_en": datetime.now().isoformat()
        }
        client.table("mensajes").insert(test_msg).execute()
        mostrar_estado("Inserción en tabla 'mensajes'", "ok")
    except Exception as e:
        mostrar_estado(f"Tabla 'mensajes' no disponible o falló la inserción: {e}", "error")

def listar_tablas(client):
    try:
        res = client.table("pg_catalog.pg_tables").select("*").execute()
        tablas = [r["tablename"] for r in res.data if not r["tablename"].startswith("pg_")]
        print("\n🗂️ Tablas encontradas en tu Supabase:")
        for t in tablas:
            print("   -", t)
        return tablas
    except Exception as e:
        mostrar_estado(f"No se pudieron listar las tablas: {e}", "error")
        return []

def run_verificacion():
    print("\n🔍 Verificando conexión a Supabase y estructura...\n")

    if not verificar_variables_entorno():
        print("\n❌ Verificación detenida. Asegúrate de tener las variables SUPABASE_URL y SUPABASE_KEY en tu .env")
        return

    client = conectar_supabase()
    if not client:
        return

    # Pruebas
    probar_tabla_contactos(client)
    probar_tabla_mensajes(client)
    tablas = listar_tablas(client)

    # Recomendaciones
    print("\n📌 Revisión de tablas esperadas:")
    esperadas = ["contactos", "mensajes", "respuestas_bot"]
    for t in esperadas:
        if t in tablas:
            mostrar_estado(f"Tabla '{t}'", "ok")
        else:
            mostrar_estado(f"Tabla '{t}'", "advertencia")

    print("\n✅ Verificación completada.")

if __name__ == "__main__":
    run_verificacion()
