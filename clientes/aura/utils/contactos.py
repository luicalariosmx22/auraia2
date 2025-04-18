from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Función para obtener los datos de un contacto
def obtener_datos_contacto(numero):
    """
    Obtiene los datos de un contacto desde la tabla `contactos` en Supabase.
    Si el contacto no existe, lo inicializa con valores predeterminados.
    """
    try:
        response = supabase.table("contactos").select("*").eq("numero", numero).execute()
        if not response.data:
            print(f"⚠️ Contacto no encontrado. Inicializando datos predeterminados para {numero}.")
            return {
                "numero": numero,
                "nombre": "",
                "foto_perfil": "",
                "ia_activada": True,
                "primer_mensaje": datetime.now().isoformat(),
                "ultimo_mensaje": datetime.now().isoformat(),
                "cantidad_mensajes": 0,
                "etiquetas": []
            }
        return response.data[0]
    except Exception as e:
        print(f"❌ Error al obtener datos del contacto {numero}: {str(e)}")
        return None

# Función para actualizar los datos de un contacto
def actualizar_datos_contacto(numero, nombre=None, foto_perfil=None, ia_activada=None, etiquetas=None):
    """
    Actualiza los datos de un contacto en la tabla `contactos` en Supabase.
    Si el contacto no existe, lo crea con los valores proporcionados.
    """
    try:
        # Obtener los datos actuales del contacto
        contacto = obtener_datos_contacto(numero)

        # Actualizar los valores
        if nombre:
            contacto["nombre"] = nombre
        if foto_perfil:
            contacto["foto_perfil"] = foto_perfil
        if ia_activada is not None:
            contacto["ia_activada"] = ia_activada
        if etiquetas:
            contacto["etiquetas"] = etiquetas

        # Actualizar la cantidad de mensajes y las fechas de los mensajes
        contacto["cantidad_mensajes"] += 1
        contacto["ultimo_mensaje"] = datetime.now().isoformat()

        # Si es el primer mensaje, actualizar la fecha del primer mensaje
        if contacto["cantidad_mensajes"] == 1:
            contacto["primer_mensaje"] = datetime.now().isoformat()

        # Guardar los datos actualizados en Supabase
        response = supabase.table("contactos").upsert(contacto).execute()
        if response.error:
            print(f"❌ Error al actualizar datos del contacto {numero}: {response.error}")
        else:
            print(f"✅ Datos del contacto {numero} actualizados correctamente.")
    except Exception as e:
        print(f"❌ Error al actualizar datos del contacto {numero}: {str(e)}")
