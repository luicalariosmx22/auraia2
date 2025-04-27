# 📁 clientes/aura/handlers/process_message.py

print("✅ process_message.py cargado correctamente al chile y ajustado para actualización real")

from datetime import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.limpieza import limpiar_mensaje
from clientes.aura.utils.historial import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.utils.supabase import supabase

def obtener_config_nora(nombre_nora):
    """
    Obtiene la configuración de Nora desde Supabase.
    """
    try:
        response = supabase.table("configuracion_bot") \
            .select("*") \
            .eq("nombre_nora", nombre_nora.lower()) \
            .execute()
        data = response.data
        return data[0] if data else {}
    except Exception as e:
        print(f"❌ Error al obtener configuración: {e}")
        return {}

def actualizar_contacto(numero_usuario, nombre_nora, mensaje_usuario, imagen_perfil=None):
    """
    Actualiza último mensaje, fecha y foto del contacto. Si no encuentra exacto, busca por variaciones.
    """
    try:
        # Intentar buscar contacto exacto
        print(f"🔍 Intentando actualizar contacto exacto para {numero_usuario} en Nora {nombre_nora}...")
        response = supabase.table("contactos") \
            .select("id") \
            .eq("telefono", numero_usuario) \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        print(f"🔍 Respuesta exacta: {response.data}")

        if not response.data:
            # Si no encontró exacto, buscar por los últimos 10 dígitos
            ultimos_10 = numero_usuario[-10:]
            print(f"🔍 Buscando contacto por últimos 10 dígitos: {ultimos_10}")
            response = supabase.table("contactos") \
                .select("id") \
                .like("telefono", f"%{ultimos_10}") \
                .eq("nombre_nora", nombre_nora) \
                .execute()
            print(f"🔍 Respuesta por últimos 10 dígitos: {response.data}")

        if response.data:
            contacto_id = response.data[0]["id"]
            update_data = {
                "ultimo_mensaje": datetime.now().isoformat(),  # Ensure timestamp is added
                "mensaje_reciente": mensaje_usuario  # Ensure recent message is updated
            }
            if imagen_perfil:
                update_data["imagen_perfil"] = imagen_perfil

            print(f"🔄 Actualizando contacto ID {contacto_id} con datos: {update_data}")
            update_response = supabase.table("contactos").update(update_data).eq("id", contacto_id).execute()
            print(f"✅ Respuesta de actualización: {update_response.data}")
            if update_response.data:
                print(f"✅ Contacto {numero_usuario} actualizado correctamente.")
            else:
                print(f"⚠️ La actualización no devolvió datos. Verifica la consulta.")
        else:
            print(f"⚠️ No se encontró contacto para {numero_usuario}. No se actualizó nada.")
    except Exception as e:
        print(f"❌ Error actualizando contacto: {e}")

def procesar_mensaje(data):
    """
    Procesa el mensaje recibido, limpia el texto, normaliza el número, obtiene historial y llama a la IA.
    """
    numero_usuario = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")
    imagen_perfil = data.get("ProfilePicUrl")  # 🔥 Ahora también leemos la foto si viene
    nombre_nora = data.get("NombreNora", "nora").lower()

    # Configuración y número real de Nora
    config = obtener_config_nora(nombre_nora)
    numero_nora = config.get("numero_nora", "5210000000000")
    print(f"🔧 Configuración para {nombre_nora} → número_nora={numero_nora}")

    # Verificar si es la primera interacción
    historial = supabase.table("historial_conversaciones") \
        .select("id") \
        .eq("telefono", numero_usuario) \
        .limit(1) \
        .execute().data

    if not historial:
        mensaje_bienvenida = config.get("mensaje_bienvenida", "").strip()
        if mensaje_bienvenida:
            print("📩 Enviando mensaje de bienvenida visible...")
            enviar_mensaje(numero_usuario, mensaje_bienvenida, nombre_usuario)
            guardar_en_historial(
                telefono=numero_usuario,
                mensaje=mensaje_bienvenida,
                origen=numero_nora,
                nombre_nora=nombre_nora,
                tipo="respuesta"
            )

    # Guardar mensaje entrante en historial
    guardar_en_historial(
        telefono=numero_usuario,
        mensaje=mensaje_usuario,
        origen=numero_usuario,
        nombre_nora=nombre_nora,
        tipo="usuario"
    )

    # Actualizar contacto con el último mensaje y foto de perfil
    # 🔥 Aquí sí funciona real
    actualizar_contacto(numero_usuario, nombre_nora, mensaje_usuario, imagen_perfil)

    # Generar respuesta desde IA con historial y contexto automáticamente manejados dentro de handle_ai
    respuesta, historial = manejar_respuesta_ai(
        mensaje_usuario=mensaje_usuario,
        numero_nora=numero_nora
    )

    if not respuesta:
        print("⚠️ No se pudo generar una respuesta. Usando mensaje predeterminado.")
        respuesta = "Lo siento, no puedo responder en este momento. Por favor, intenta más tarde."

    # Guardar respuesta en historial
    guardar_en_historial(
        telefono=numero_usuario,
        mensaje=respuesta,
        origen=numero_nora,
        nombre_nora=nombre_nora,
        tipo="respuesta"
    )

    # Enviar respuesta al usuario
    enviar_mensaje(numero_usuario, respuesta, nombre_usuario)
    return respuesta
