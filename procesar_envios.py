print("✅ procesar_envios.py cargado correctamente")

import time
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
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
    """
    Leer contactos desde Supabase.
    """
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
    """
    Guardar historial en Supabase.
    """
    print(f"🔍 Intentando guardar historial para {numero} en {nombre_nora}...")
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": numero,
            "mensaje": mensaje["texto"],
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
    """
    Leer historial desde Supabase.
    """
    print(f"🔍 Intentando leer historial para {numero} en {nombre_nora}...")
    try:
        response = supabase.table("historial_conversaciones").select("*").eq("nombre_nora", nombre_nora).eq("telefono", numero).execute()
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
    """
    Procesar envíos programados desde Supabase.
    """
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
                print(f"📦 Procesando envío: {envio}")
                try:
                    # Verifica la fecha y hora del envío
                    fecha_hora = datetime.strptime(f"{envio['fecha']} {envio['hora']}", "%Y-%m-%d %H:%M")
                    print(f"🕒 Fecha y hora del envío: {fecha_hora}, ahora: {ahora}")
                    if fecha_hora > ahora:
                        print(f"⏳ Envío programado para el futuro. Saltando: {envio['id']}")
                        continue

                    print(f"📤 Enviando mensaje programado a {envio['numero']}")

                    # Leer historial existente
                    historial = leer_historial(envio["nombre_nora"], envio["numero"])
                    print(f"✅ Historial actual para {envio['numero']}: {historial}")

                    # Agregar el mensaje al historial
                    historial.append({
                        "emisor": "nora",
                        "texto": envio["mensaje"],
                        "hora": ahora.strftime("%H:%M")
                    })

                    # Verificar y manejar el contacto
                    contactos = leer_contactos(envio["nombre_nora"])
                    contacto = next((c for c in contactos if c["telefono"] == envio["numero"]), {})
                    print(f"✅ Contacto encontrado: {contacto}")

                    # Generar respuesta automática si IA está activada
                    if contacto.get("ia", False):
                        respuesta = f"Respuesta automática a: {envio['mensaje']}"
                        historial.append({
                            "emisor": "nora",
                            "texto": respuesta,
                            "hora": ahora.strftime("%H:%M")
                        })
                        print(f"🤖 Respuesta automática generada: {respuesta}")

                    # Verificar y manejar el campo nombre_nora
                    nombre_nora = envio.get("nombre_nora", "Nora")
                    print(f"🔍 Verificando nombre_nora: {nombre_nora}")

                    # Guardar el historial en la base de datos
                    guardar_historial(nombre_nora, envio["numero"], historial)

                    # Marcar el envío como completado
                    print(f"🗑️ Eliminando envío completado: {envio['id']}")
                    supabase.table("envios_programados").delete().eq("id", envio["id"]).execute()
                    print(f"✅ Envío completado y eliminado: {envio['id']}")

                except Exception as e:
                    print(f"❌ Error al procesar envío {envio['id']}: {str(e)}")

        except Exception as e:
            print(f"❌ Error general al procesar envíos: {str(e)}")

        # Esperar antes de procesar nuevamente
        print("⏳ Esperando 30 segundos antes de la próxima iteración...")
        time.sleep(30)

if __name__ == "__main__":
    print("🕒 Procesador de envíos iniciado")
    procesar_envios()
