print("✅ Script de actualización de contactos iniciado")

from dotenv import load_dotenv
from supabase import create_client
import os

# Configuración de Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def actualizar_contactos_existentes(nombre_nora):
    print(f"🔍 Actualizando contactos para Nora: {nombre_nora}")
    try:
        # Obtener todos los contactos de la Nora
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        contactos = response.data or []
        print(f"✅ Contactos encontrados: {len(contactos)}")

        for contacto in contactos:
            telefono = contacto.get("telefono")
            if not telefono:
                print(f"⚠️ Contacto sin teléfono. ID: {contacto.get('id')}")
                continue

            # Buscar el historial de este contacto
            historial_response = supabase.table("historial_conversaciones") \
                .select("*") \
                .eq("telefono", telefono) \
                .order("hora", desc=True) \
                .limit(1) \
                .execute()

            historial = historial_response.data

            if historial:
                ultimo = historial[0]
                update_data = {
                    "ultimo_mensaje": ultimo["hora"],
                    "mensaje_reciente": ultimo["mensaje"]
                }
                supabase.table("contactos").update(update_data).eq("telefono", telefono).eq("nombre_nora", nombre_nora).execute()
                print(f"✅ Contacto {telefono} actualizado con último mensaje.")
            else:
                print(f"⚠️ Sin historial encontrado para {telefono}")

    except Exception as e:
        print(f"❌ Error actualizando contactos: {e}")

# Ejecución manual
if __name__ == "__main__":
    actualizar_contactos_existentes("aura")  # 👈🏻 Aquí pones el nombre_nora que quieres actualizar
