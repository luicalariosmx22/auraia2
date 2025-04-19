print("✅ procesar_envios.py cargado correctamente")

import time
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from utils.normalizador import normalizar_numero  # ✅ Importado
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL o SUPABASE_KEY no están configurados correctamente.")
else:
    print("✅ Conexión con Supabase configurada correctamente.")

def leer_contactos(nombre_nora):
    print(f"🔍 Intentando leer contactos para {nombre_nora}...")
    try:
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"⚠️ No se encontraron contactos para {nombre_nora}.")
            return []
        print(f"✅ Contactos cargados: {len(response.data)}")
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return []

def guardar_historial(nombre_nora, numero, mensajes):
    print(f"🔍 Intentando guardar historial para {numero} en {nombre_nora}...")
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": numero,
            "mensaje": mensaje.get("texto") or mensaje.get("mensaje"),
            "emisor": mensaje["emisor"],
            "hora": mensaje["hora"],
            "timestamp": datetime.now()
        }
        for mensaje in mensajes
    ]
    print(f"📋 Registros a guardar: {registros}")
    try:
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if not response.data:
            print(f"⚠️ No se pudo guardar el historial para {numero}.")
        else:
            print(f"✅ Historial guardado correctamente para {numero}.")
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

def leer_historial(nombre_nora, numero):
    numero = normalizar_numero(numero)  # ✅ Normalización agregada
    print(f"🔍 Intentando leer historial para {numero} en {nombre_nora}...")
    try:
        response = (
            supabase.table("historial_conversaciones")
            .select("*")
            .eq("nombre_nora", nombre_nora)
            .eq("telefono", numero)
            .order("hora", desc=False)
            .execute()
        )
        if not response.data:
            print(f"⚠️ No se encontró historial para {numero}.")
            return []
        print(f"✅ Historial cargado: {len(response.data)} registros.")
        return [
            {
                "emisor": registro["emisor"],
                "texto": registro["mensaje"],
                "hora": registro["hora"]
            }
            for registro in response.data
        ]
    except Exception as e:
        print(f"❌ Error al cargar historial: {str(e)}")
        return []

def procesar_envios():
    print("🕒 Iniciando procesamiento de envíos programados...")
    while True:
        try:
            print("🔍 Consultando envíos programados...")
            response = supabase.table("envios_programados").select("*").execute()
            if not response.data:
                print("⚠️ No hay envíos programados.")
                time.sleep(30)
                continue

            pendientes = response.data
            print(f"✅ Envíos pendientes encontrados: {len(pendientes)}")
            ahora = datetime.now()

            for envio in pendientes:
                try:
                    numero = normalizar_numero(envio["numero"])  # ✅ Normalizar número
                    fecha_hora = datetime.strptime(f"{envio['fecha']} {envio['hora']}", "%Y-%m-%d %H:%M")
                    if fecha_hora > ahora:
                        print(f"⏳ Envío programado para el futuro. Saltando: {envio['id']}")
                        continue

                    print(f"📤 Enviando mensaje programado a {numero}")
                    historial = leer_historial(envio["nombre_nora"], numero)
                    historial.append({
                        "emisor": "nora",
                        "texto": envio["mensaje"],
                        "hora": ahora.strftime("%H:%M")
                    })

                    contactos = leer_contactos(envio["nombre_nora"])
                    contacto = next((c for c in contactos if normalizar_numero(c["telefono"]) == numero), {})
                    print(f"✅ Contacto encontrado: {contacto}")

                    if contacto.get("ia_activada", False):  # ✅ Campo correcto
                        respuesta = f"Respuesta automática a: {envio['mensaje']}"
                        historial.append({
                            "emisor": "nora",
                            "texto": respuesta,
                            "hora": ahora.strftime("%H:%M")
                        })
                        print(f"🤖 Respuesta automática generada: {respuesta}")

                    nombre_nora = envio.get("nombre_nora", "Nora")
                    guardar_historial(nombre_nora, numero, historial)

                    supabase.table("envios_programados").delete().eq("id", envio["id"]).execute()
                    print(f"✅ Envío completado y eliminado: {envio['id']}")

                except Exception as e:
                    print(f"❌ Error al procesar envío {envio['id']}: {str(e)}")

        except Exception as e:
            print(f"❌ Error general al procesar envíos: {str(e)}")

        print("⏳ Esperando 30 segundos antes de la próxima iteración...")
        time.sleep(30)

if __name__ == "__main__":
    print("🕒 Procesador de envíos iniciado")
    procesar_envios()
