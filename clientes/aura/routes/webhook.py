# 📁 clientes/aura/routes/webhook.py

from flask import Blueprint, request
from datetime import datetime
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.historial import guardar_en_historial, guardar_en_historial_batch  # ✅ Asegúrate de importar esto

webhook_bp = Blueprint("webhook", __name__)

def obtener_historial_usuario(telefono):
    """
    Recupera el historial de un usuario desde la tabla historial_conversaciones.
    """
    try:
        print(f"🔍 Buscando historial para el teléfono: {telefono}")
        response = supabase.table("historial_conversaciones").select("*").eq("telefono", telefono).order("timestamp", ascending=True).execute()
        print(f"🔍 Respuesta de Supabase: {response.data}")
        if response.data:
            historial = [{"role": "user" if m["tipo"] == "recibido" else "assistant", "content": m["mensaje"]} for m in response.data]
            return historial
        return []  # Devuelve una lista vacía si no hay historial
    except Exception as e:
        print(f"❌ Error al obtener historial del usuario {telefono}: {e}")
        return []

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
        try:
            response = supabase.table("configuracion_bot").select("nombre_nora").eq("numero_nora", numero_nora).execute()
            resultado = response.data or []
        except Exception as e:
            print(f"❌ Error al consultar Supabase: {e}")
            return "Error al consultar la base de datos", 500

        if resultado:
            nombre_nora_detectado = resultado[0]["nombre_nora"]
            print(f"🎯 Detectado nombre_nora automáticamente: {nombre_nora_detectado}")
            data["NombreNora"] = nombre_nora_detectado  # ✅ Sobrescribir en data
        else:
            print(f"⚠️ No se encontró configuración para el número: {numero_nora}")
            return {"error": f"El número {numero_nora} no está configurado en la base de datos."}, 400

        print(f"🎯 NombreNora validado: '{data['NombreNora']}'")

        # 📞 Obtener número, nombre y foto del emisor
        telefono_usuario = normalizar_numero(data.get("From", ""))
        if not telefono_usuario:
            print("❌ Número de teléfono no válido.")
            return {"error": "Número de teléfono no válido"}, 400

        nombre_emisor = data.get("ProfileName", None)
        imagen_perfil = data.get("ProfilePicUrl", None)
        mensaje_usuario = data.get("Body", "")
        nombre_nora = data["NombreNora"]

        # 🔍 Verificar si el contacto ya existe
        response = supabase.table("contactos").select("*").eq("telefono", telefono_usuario).execute()
        contacto_existente = response.data[0] if response.data else None

        if contacto_existente:
            print(f"🔄 Actualizando contacto existente: {telefono_usuario}")
            supabase.table("contactos").update({
                "nombre": nombre_emisor or contacto_existente["nombre"],
                "imagen_perfil": imagen_perfil or contacto_existente.get("imagen_perfil"),
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_reciente": mensaje_usuario
            }).eq("telefono", telefono_usuario).execute()
        else:
            print(f"🆕 Guardando nuevo contacto: {telefono_usuario}")
            supabase.table("contactos").insert({
                "telefono": telefono_usuario,
                "nombre": nombre_emisor or f"Usuario {telefono_usuario[-4:]}",
                "imagen_perfil": imagen_perfil,
                "primer_mensaje": datetime.now().isoformat(),
                "ultimo_mensaje": datetime.now().isoformat(),
                "mensaje_reciente": mensaje_usuario,
                "nombre_nora": nombre_nora,
                "etiquetas": ["nuevo"]
            }).execute()

        # Recuperar historial del usuario
        historial = obtener_historial_usuario(telefono_usuario)
        print(f"🔍 Historial recuperado: {historial}")

        # Generar respuesta con IA
        respuesta, historial_actualizado = manejar_respuesta_ai(mensaje_usuario, historial)
        if not respuesta:
            print("🟡 No se generó una respuesta. Posiblemente sin IA o sin conocimiento.")
            return {"message": "No se pudo generar una respuesta"}, 200

        # ✅ Guardar historial manualmente si hay respuesta
        print(f"✅ Respuesta enviada: {respuesta}")

        guardar_en_historial_batch([
            {
                "telefono": telefono_usuario,
                "mensaje": mensaje_usuario,
                "origen": telefono_usuario,
                "nombre_nora": nombre_nora,
                "tipo": "recibido",
                "nombre": nombre_emisor or telefono_usuario
            },
            {
                "telefono": telefono_usuario,
                "mensaje": respuesta,
                "origen": "Nora",
                "nombre_nora": nombre_nora,
                "tipo": "enviado",
                "nombre": "Nora"
            }
        ])

        return {"message": respuesta}, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return {"error": "Error interno"}, 500
