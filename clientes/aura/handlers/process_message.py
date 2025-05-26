# 📁 clientes/aura/handlers/process_message.py

print("✅ process_message.py cargado correctamente al chile y ajustado para actualización real")

from datetime import datetime
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.limpieza import limpiar_mensaje
from clientes.aura.utils.historial import guardar_en_historial
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.utils.buscar_conocimiento import construir_menu_desde_etiquetas, obtener_conocimiento_por_etiqueta
from clientes.aura.utils.supabase_client import supabase

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
construir_menu_desde_etiquetas
def actualizar_contacto(numero_usuario, nombre_nora, mensaje_usuario, imagen_perfil=None, nombre_contacto=None):
    """
    Actualiza último mensaje, fecha y foto del contacto. Si no existe, lo crea automáticamente.
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
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_reciente": mensaje_usuario
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
            # 🔥 No existe: crear nuevo contacto automáticamente
            print(f"🆕 Contacto no encontrado. Creando nuevo contacto para {numero_usuario} en Nora {nombre_nora}...")
            nuevo_contacto = {
                "telefono": numero_usuario,
                "nombre_nora": nombre_nora,
                "ultimo_mensaje": datetime.now().isoformat(),  # Fixed key
                "mensaje_reciente": mensaje_usuario  # Fixed key
            }
            if nombre_contacto:
                nuevo_contacto["nombre"] = nombre_contacto  # ✅ La columna REAL es 'nombre'
            if imagen_perfil:
                nuevo_contacto["imagen_perfil"] = imagen_perfil

            print(f"➕ Creando nuevo contacto con datos: {nuevo_contacto}")
            insert_response = supabase.table("contactos").insert(nuevo_contacto).execute()
            print(f"✅ Respuesta de creación: {insert_response.data}")

    except Exception as e:
        print(f"❌ Error actualizando/creando contacto: {e}")

def procesar_mensaje(data):
    """
    Procesa el mensaje recibido, limpia el texto, normaliza el número, obtiene historial y llama a la IA.
    """
    numero_usuario = normalizar_numero(data.get("From"))
    mensaje_usuario = limpiar_mensaje(data.get("Body"))
    nombre_usuario = data.get("ProfileName", "Usuario")
    imagen_perfil = data.get("ProfilePicUrl")  # 🔥 Ahora también leemos la foto si viene
    numero_nora_recibido = normalizar_numero(data.get("To"))

    # 🔍 Buscar en Supabase cuál es el nombre_nora usando el número To
    try:
        response = supabase.table("configuracion_bot") \
            .select("nombre_nora, numero_nora") \
            .eq("numero_nora", numero_nora_recibido) \
            .limit(1) \
            .execute()
        if response.data:
            nombre_nora = response.data[0]["nombre_nora"].lower()
            numero_nora = response.data[0]["numero_nora"]
            print(f"🔧 Configuración encontrada: nombre_nora={nombre_nora}, numero_nora={numero_nora}")
        else:
            print(f"⚠️ No se encontró configuración para {numero_nora_recibido}. Usando valor por defecto.")
            nombre_nora = "nora"
            numero_nora = numero_nora_recibido
    except Exception as e:
        print(f"❌ Error buscando configuración: {e}")
        nombre_nora = "nora"
        numero_nora = numero_nora_recibido

    # Verificar si es la primera interacción
    historial = supabase.table("historial_conversaciones") \
        .select("id") \
        .eq("telefono", numero_usuario) \
        .eq("nombre_nora", nombre_nora) \
        .limit(1) \
        .execute().data

    if not historial:
        mensaje_bienvenida = config.get("mensaje_bienvenida", "").strip() if 'config' in locals() else ""
        if mensaje_bienvenida:
            print("📩 Enviando mensaje de bienvenida visible...")
            enviar_mensaje(numero_usuario, mensaje_bienvenida)
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
    actualizar_contacto(numero_usuario, nombre_nora, mensaje_usuario, imagen_perfil, nombre_contacto=nombre_usuario)

    # --- MENÚ DE CONOCIMIENTO (etiquetas) ---
    # Detectar si el mensaje es para mostrar el menú
    if mensaje_usuario.lower() in ["menu", "opciones", "categorías"]:
        mensaje_menu = construir_menu_desde_etiquetas(nombre_nora)
        enviar_mensaje(numero_usuario, mensaje_menu)
        guardar_en_historial(numero_usuario, mensaje_menu, numero_nora, nombre_nora, "respuesta")
        return mensaje_menu

    # Detectar si es respuesta a un menú (número o etiqueta)
    try:
        etiquetas_res = supabase.table("etiquetas_nora") \
            .select("etiqueta") \
            .eq("nombre_nora", nombre_nora) \
            .eq("activo", True) \
            .execute()

        etiquetas = [et["etiqueta"] for et in etiquetas_res.data] if etiquetas_res.data else []
        seleccion = mensaje_usuario.strip().lower()

        if seleccion.isdigit():
            index = int(seleccion) - 1
            if 0 <= index < len(etiquetas):
                etiqueta_seleccionada = etiquetas[index]
            else:
                etiqueta_seleccionada = None
        else:
            etiqueta_seleccionada = next((et for et in etiquetas if seleccion in et.lower()), None)

        if etiqueta_seleccionada:
            contenido = obtener_conocimiento_por_etiqueta(nombre_nora, etiqueta_seleccionada)
            if contenido:
                enviar_mensaje(numero_usuario, contenido)
                guardar_en_historial(numero_usuario, contenido, numero_nora, nombre_nora, "respuesta")
                return contenido

    except Exception as e:
        print(f"❌ Error interpretando respuesta al menú de conocimiento: {e}")

    # Generar respuesta desde IA
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
    enviar_mensaje(numero_usuario, respuesta)

    # 🧠 Detectar si el último bloque fue un MENÚ y responder sin IA
    try:
        historial_menus = supabase.table("historial_conversaciones") \
            .select("mensaje, origen, tipo") \
            .eq("telefono", numero_usuario) \
            .eq("nombre_nora", nombre_nora) \
            .order("timestamp", desc=True) \
            .limit(5) \
            .execute().data

        ultimo_menu = next((h for h in historial_menus if h["origen"] == numero_nora and h["tipo"] == "respuesta" and "¿" in h["mensaje"]), None)

        if ultimo_menu:
            print("🧭 Último mensaje fue un MENÚ. Intentando interpretar respuesta del usuario...")

            # Buscar menú correspondiente
            bloques_menu = supabase.table("conocimiento_nora") \
                .select("*") \
                .eq("nombre_nora", nombre_nora) \
                .eq("origen", "menu") \
                .eq("activo", True) \
                .execute().data

            # Match exacto del último contenido
            menu_bloque = next((b for b in bloques_menu if b["contenido"] in ultimo_menu["mensaje"]), None)

            if menu_bloque:
                opciones = menu_bloque.get("opciones", [])
                etiquetas = menu_bloque.get("etiquetas", [])
                seleccion = mensaje_usuario.strip().lower()

                # Match por número ("1", "2", ...)
                if seleccion.isdigit():
                    idx = int(seleccion) - 1
                    if 0 <= idx < len(opciones):
                        opcion_elegida = opciones[idx]
                    else:
                        opcion_elegida = None
                else:
                    # Match por texto aproximado
                    opcion_elegida = next((opt for opt in opciones if seleccion in opt.lower()), None)

                if opcion_elegida:
                    print(f"✅ Opción detectada: {opcion_elegida}")

                    # Buscar bloque de conocimiento relacionado
                    resultados = supabase.table("conocimiento_nora") \
                        .select("*") \
                        .eq("nombre_nora", nombre_nora) \
                        .eq("activo", True) \
                        .execute().data

                    coincidencia = next(
                        (b for b in resultados if opcion_elegida.lower() in b.get("contenido", "").lower()
                         or opcion_elegida.lower() in " ".join(b.get("etiquetas", [])).lower()),
                        None
                    )

                    if coincidencia:
                        respuesta = coincidencia["contenido"]
                        guardar_en_historial(numero_usuario, respuesta, numero_nora, nombre_nora, "respuesta")
                        enviar_mensaje(numero_usuario, respuesta)
                        return respuesta

                print("⚠️ No se encontró opción válida o bloque relacionado.")
                fallback = "No entendí tu respuesta. ¿Puedes elegir una opción del menú anterior?"
                guardar_en_historial(numero_usuario, fallback, numero_nora, nombre_nora, "respuesta")
                enviar_mensaje(numero_usuario, fallback)
                return fallback

    except Exception as e:
        print(f"❌ Error interpretando menú: {e}")

    return respuesta
