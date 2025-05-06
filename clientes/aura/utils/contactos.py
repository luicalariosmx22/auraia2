from datetime import datetime
from clientes.aura.utils.supabase_client import supabase
from dotenv import load_dotenv
import os
from utils.normalizador import normalizar_numero  # ✅ Importado

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Función para obtener los datos de un contacto
def obtener_datos_contacto(numero):
    numero = normalizar_numero(numero)  # ✅ Normalizar antes de consultar

    try:
        response = supabase.table("contactos").select("*").eq("telefono", numero).execute()
        if not response.data:
            print(f"⚠️ Contacto no encontrado. Inicializando datos predeterminados para {numero}.")
            return {
                "telefono": numero,
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
    numero = normalizar_numero(numero)  # ✅ Normalizar también aquí

    try:
        contacto = obtener_datos_contacto(numero)

        if nombre:
            contacto["nombre"] = nombre
        if foto_perfil:
            contacto["foto_perfil"] = foto_perfil
        if ia_activada is not None:
            contacto["ia_activada"] = ia_activada
        if etiquetas:
            contacto["etiquetas"] = etiquetas

        contacto["cantidad_mensajes"] += 1
        contacto["ultimo_mensaje"] = datetime.now().isoformat()

        if contacto["cantidad_mensajes"] == 1:
            contacto["primer_mensaje"] = datetime.now().isoformat()

        response = supabase.table("contactos").upsert(contacto).execute()
        if not response.data:
            print(f"❌ Error al actualizar datos del contacto {numero}: {not response.data}")
        else:
            print(f"✅ Datos del contacto {numero} actualizados correctamente.")
    except Exception as e:
        print(f"❌ Error al actualizar datos del contacto {numero}: {str(e)}")
