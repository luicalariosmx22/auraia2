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

def leer_contactos(nombre_nora):
    """
    Leer contactos desde Supabase.
    """
    try:
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:  # Verifica si no hay datos
            print(f"⚠️ No se encontraron contactos para {nombre_nora}.")
            return []
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return []

def guardar_historial(nombre_nora, numero, mensajes):
    """
    Guardar historial en Supabase.
    """
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": numero,
            "mensaje": mensaje["texto"],
            "origen": mensaje["origen"],
            "hora": mensaje["hora"]
        }
        for mensaje in mensajes
    ]
    try:
        response = supabase.table("historial_conversaciones").insert(registros).execute()
        if not response.data:  # Verifica si no se insertaron datos
            print(f"⚠️ No se pudo guardar el historial para {numero}.")
        else:
            print(f"✅ Historial guardado para {numero}")
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

def leer_historial(nombre_nora, numero):
    """
    Leer historial desde Supabase.
    """
    try:
        response = supabase.table("historial_conversaciones").select("*").eq("nombre_nora", nombre_nora).eq("telefono", numero).execute()
        if not response.data:  # Verifica si no hay datos
            print(f"⚠️ No se encontró historial para {numero}.")
            return []
        return [
            {
                "origen": registro["origen"],
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
    while True:
        try:
            response = supabase.table("envios_programados").select("*").execute()
            if not response.data:  # Verifica si no hay datos
                print("⚠️ No hay envíos programados.")
                time.sleep(30)
                continue

            pendientes = response.data
            ahora = datetime.now()

            for envio in pendientes:
                fecha_hora = datetime.strptime(f"{envio['fecha']} {envio['hora']}", "%Y-%m-%d %H:%M")
                if fecha_hora <= ahora:
                    print(f"📤 Enviando mensaje programado a {envio['numero']}")
                    historial = leer_historial(envio["nombre_nora"], envio["numero"])
                    historial.append({
                        "origen": "nora",
                        "texto": envio["mensaje"],
                        "hora": ahora.strftime("%H:%M")
                    })

                    contactos = leer_contactos(envio["nombre_nora"])
                    contacto = next((c for c in contactos if c["telefono"] == envio["numero"]), {})

                    if contacto.get("ia", False):
                        respuesta = f"Respuesta automática a: {envio['mensaje']}"
                        historial.append({
                            "origen": "nora",
                            "texto": respuesta,
                            "hora": ahora.strftime("%H:%M")
                        })

                    guardar_historial(envio["nombre_nora"], envio["numero"], historial)

                    # Marcar el envío como completado
                    supabase.table("envios_programados").delete().eq("id", envio["id"]).execute()

        except Exception as e:
            print(f"❌ Error al procesar envíos: {str(e)}")

        time.sleep(30)

if __name__ == "__main__":
    print("🕒 Procesador de envíos iniciado")
    procesar_envios()
