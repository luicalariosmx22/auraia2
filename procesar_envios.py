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
            "nombre_nora": nombre_nora,  # Incluye el campo 'nombre_nora'
            "telefono": numero,
            "mensaje": mensaje["texto"],
            "emisor": mensaje["origen"],  # Cambiado de 'origen' a 'emisor' para coincidir con la tabla
            "hora": mensaje["hora"],  # Asegúrate de que 'hora' sea un timestamp válido
            "timestamp": datetime.now()  # Agrega un timestamp actual
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
                "emisor": registro["emisor"],  # Cambiado de 'origen' a 'emisor'
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
            # Obtén los envíos pendientes desde Supabase
            response = supabase.table("envios_programados").select("*").execute()
            if not response.data:  # Si no hay datos, imprime un mensaje
                print("⚠️ No hay envíos programados.")
                time.sleep(30)
                continue

            pendientes = response.data
            ahora = datetime.now()

            for envio in pendientes:
                # Verifica la fecha y hora del envío
                fecha_hora = datetime.strptime(f"{envio['fecha']} {envio['hora']}", "%Y-%m-%d %H:%M")
                if fecha_hora <= ahora:
                    print(f"📤 Enviando mensaje programado a {envio['numero']}")

                    # Leer historial existente
                    historial = leer_historial(envio["nombre_nora"], envio["numero"])
                    print(f"✅ Historial actual para {envio['numero']}: {historial}")

                    # Agregar el mensaje al historial
                    historial.append({
                        "emisor": "nora",  # Cambiado de 'origen' a 'emisor'
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
                            "emisor": "nora",  # Cambiado de 'origen' a 'emisor'
                            "texto": respuesta,
                            "hora": ahora.strftime("%H:%M")
                        })
                        print(f"🤖 Respuesta automática generada: {respuesta}")

                    # Verificar y manejar el campo nombre_nora
                    nombre_nora = envio.get("nombre_nora", "Nora")  # Valor predeterminado si no existe
                    print(f"Verificando nombre_nora: {nombre_nora}")

                    # Guardar el historial en la base de datos
                    guardar_historial(nombre_nora, envio["numero"], historial)

                    # Marcar el envío como completado
                    supabase.table("envios_programados").delete().eq("id", envio["id"]).execute()
                    print(f"✅ Envío completado y eliminado de la tabla: {envio['id']}")

        except Exception as e:
            print(f"❌ Error al procesar envíos: {str(e)}")

        # Esperar antes de procesar nuevamente
        time.sleep(30)

if __name__ == "__main__":
    print("🕒 Procesador de envíos iniciado")
    procesar_envios()
