# 📁 clientes/aura/routes/webhook.py

import logging
from flask import Blueprint, request
from datetime import datetime
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.historial import guardar_en_historial_batch
from clientes.aura.utils.twilio import enviar_mensaje_twilio

# Configurar el nivel de logs de OpenAI
logging.getLogger("openai").setLevel(logging.WARNING)

webhook_bp = Blueprint("webhook", __name__)

def obtener_historial_usuario(telefono):
    try:
        print(f"🔍 Buscando historial para el teléfono: {telefono}")
        response = supabase.table("historial_conversaciones").select("*").eq("telefono", telefono).order("timestamp", desc=False).execute()
        if response.data:
            print("✅ Conversaciones cargadas.")
            historial = [{"role": "user" if m["tipo"] == "recibido" else "assistant", "content": m["mensaje"]} for m in response.data]
            return historial
        print("⚠️ No se encontraron conversaciones.")
        return []
    except Exception as e:
        print(f"❌ Error al obtener historial del usuario {telefono}: {e}")
        return []

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)

        numero_nora = normalizar_numero(data.get("To", ""))
        print(f"📞 Número de Nora detectado: {numero_nora}")

        # Consulta a Supabase para obtener el nombre y el número de Nora
        response = supabase.table("configuracion_bot").select("nombre_nora, numero_nora").eq("numero_nora", numero_nora).execute()
        resultado = response.data or []

        if resultado:
            nombre_nora_detectado = resultado[0]["nombre_nora"]
            numero_nora_remitente = resultado[0]["numero_nora"]
            print(f"🎯 Detectado nombre_nora automáticamente: {nombre_nora_detectado}")
            print(f"📞 Número de WhatsApp de la Nora: {numero_nora_remitente}")
        else:
            print(f"⚠️ No se encontró configuración para el número: {numero_nora}")
            return {"error": f"El número {numero_nora} no está configurado en la base de datos."}, 400

        telefono_usuario = normalizar_numero(data.get("From", ""))
        print(f"📞 Número de teléfono del usuario: {telefono_usuario}")
        if not telefono_usuario:
            print("❌ Número de teléfono no válido.")
            return {"error": "Número de teléfono no válido"}, 400

        mensaje_usuario = data.get("Body", "")
        historial = obtener_historial_usuario(telefono_usuario)

        if not historial:
            print("⚠️ No se encontró historial. Generando respuesta sin contexto.")

        respuesta, historial_actualizado = manejar_respuesta_ai(mensaje_usuario, historial)
        if not respuesta:
            print(f"🟡 No se generó una respuesta para el mensaje: {mensaje_usuario}")
            print(f"Historial proporcionado: {historial}")
            return {"message": "No se pudo generar una respuesta"}, 200

        # Enviar mensaje con el número de WhatsApp de la Nora
        try:
            enviar_mensaje_twilio(telefono_usuario, respuesta, numero_nora_remitente)
        except Exception as e:
            print(f"❌ Error al enviar mensaje con Twilio: {e}")
            return {"error": "Error al enviar mensaje con Twilio"}, 500

        guardar_en_historial_batch([
            {"telefono": telefono_usuario, "mensaje": mensaje_usuario, "origen": telefono_usuario, "tipo": "recibido"},
            {"telefono": telefono_usuario, "mensaje": respuesta, "origen": "Nora", "tipo": "enviado"}
        ])

        return {"message": respuesta}, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return {"error": "Error interno"}, 500
