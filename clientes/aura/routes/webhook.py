# 📁 clientes/aura/routes/webhook.py

from flask import Blueprint, request
from datetime import datetime
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.historial import guardar_en_historial  # ✅ Asegúrate de importar esto

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 📨 Datos crudos del webhook
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)

        # 📞 Obtener número del destinatario (es el número de Nora)
        numero_nora = normalizar_numero(data.get("To", ""))
        print(f"📞 Número de Nora detectado: {numero_nora}")

        # 🔍 Buscar el nombre_nora correspondiente en Supabase
        response = (
            supabase.table("configuracion_bot")
            .select("nombre_nora")
            .eq("numero_nora", numero_nora)
            .execute()
        )

        resultado = response.data or []
        if resultado:
            nombre_nora_detectado = resultado[0]["nombre_nora"]
            print(f"🎯 Detectado nombre_nora automáticamente: {nombre_nora_detectado}")
            data["NombreNora"] = nombre_nora_detectado  # ✅ Sobrescribir en data
        else:
            # 🚨 Registro adicional para depuración
            print(f"⚠️ No se encontró configuración para el número: {numero_nora}")
            print("🔍 Verifica si el número está registrado correctamente en la tabla 'configuracion_bot'.")
            print("🔍 Datos recibidos:", data)

            # Lanzar una excepción si el número no está configurado
            raise ValueError(f"El número {numero_nora} no está configurado en la base de datos.")

        print(f"🎯 NombreNora validado: '{data['NombreNora']}'")

        # 📞 Obtener número, nombre y foto del emisor
        telefono_usuario = normalizar_numero(data.get("From", ""))
        nombre_emisor = data.get("ProfileName", None)  # Capturar el nombre del perfil
        imagen_perfil = data.get("ProfilePicUrl", None)  # Capturar la URL de la imagen de perfil
        mensaje_usuario = data.get("Body", "")
        nombre_nora = data["NombreNora"]

        # 🔍 Verificar si el contacto ya existe
        response = supabase.table("contactos").select("*").eq("telefono", telefono_usuario).execute()
        contacto_existente = response.data[0] if response.data else None

        if contacto_existente:
            # 🛠️ Actualizar contacto existente
            print(f"🔄 Actualizando contacto existente: {telefono_usuario}")
            supabase.table("contactos").update({
                "nombre": nombre_emisor or contacto_existente["nombre"],  # Reemplazar nombre si ProfileName está disponible
                "imagen_perfil": imagen_perfil or contacto_existente.get("imagen_perfil"),  # Actualizar imagen si está disponible
                "ultimo_mensaje": datetime.now().isoformat(),  # Actualizar fecha del último mensaje
                "mensaje_reciente": mensaje_usuario  # Guardar el último mensaje recibido
            }).eq("telefono", telefono_usuario).execute()
        else:
            # 🆕 Guardar el contacto si no existe
            print(f"🆕 Guardando nuevo contacto: {telefono_usuario}")
            supabase.table("contactos").insert({
                "telefono": telefono_usuario,
                "nombre": nombre_emisor or f"Usuario {telefono_usuario[-4:]}",  # Nombre del perfil o genérico
                "imagen_perfil": imagen_perfil,  # Guardar la URL de la imagen de perfil
                "primer_mensaje": datetime.now().isoformat(),
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_reciente": mensaje_usuario,  # Guardar el último mensaje recibido
                "nombre_nora": nombre_nora,
                "etiquetas": ["nuevo"]  # Etiqueta inicial para nuevos contactos
            }).execute()

        # 🧠 Procesar el mensaje
        respuesta = procesar_mensaje(data)

        # ✅ Guardar historial manualmente si hay respuesta
        if respuesta:
            print(f"✅ Respuesta enviada: {respuesta}")

            # 📥 Historial del mensaje recibido
            guardar_en_historial(
                telefono=telefono_usuario,
                mensaje=mensaje_usuario,
                origen=telefono_usuario,
                nombre_nora=nombre_nora,
                tipo="recibido",
                nombre=nombre_emisor or telefono_usuario
            )

            # 📤 Historial de la respuesta enviada
            guardar_en_historial(
                telefono=telefono_usuario,
                mensaje=respuesta,
                origen="Nora",
                nombre_nora=nombre_nora,
                tipo="enviado",
                nombre="Nora"
            )

        else:
            print("🟡 No se generó una respuesta. Posiblemente sin IA o sin conocimiento.")

        return respuesta or "", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
