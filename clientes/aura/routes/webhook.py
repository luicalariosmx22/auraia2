# 📁 clientes/aura/routes/webhook.py

import logging
from flask import Blueprint, request
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.historial import guardar_en_historial_batch
from clientes.aura.utils.twilio import enviar_mensaje_twilio

logging.getLogger("openai").setLevel(logging.WARNING)

webhook_bp = Blueprint("webhook", __name__)

def obtener_historial_usuario(telefono):
    try:
        print(f"🔍 Buscando historial para el teléfono: {telefono}")
        response = supabase.table("historial_conversaciones") \
            .select("*") \
            .eq("telefono", telefono) \
            .order("timestamp", desc=False) \
            .execute()
        if response.data:
            print("✅ Conversaciones cargadas.")
            return [
                {"role": "user" if m["tipo"] == "recibido" else "assistant", "content": m["mensaje"]}
                for m in response.data
            ]
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
        telefono_usuario = normalizar_numero(data.get("From", ""))
        mensaje_usuario = data.get("Body", "")

        if not telefono_usuario:
            return {"error": "Número de teléfono no válido"}, 400

        # Obtener nombre de la Nora
        response = supabase.table("configuracion_bot") \
            .select("nombre_nora, numero_nora") \
            .eq("numero_nora", numero_nora) \
            .limit(1) \
            .execute()
        resultado = response.data or []

        if not resultado:
            return {"error": f"El número {numero_nora} no está configurado en la base de datos."}, 400

        nombre_nora = resultado[0]["nombre_nora"]
        numero_nora_real = resultado[0]["numero_nora"]

        historial = obtener_historial_usuario(telefono_usuario)

        respuesta, historial_actualizado = manejar_respuesta_ai(
            mensaje_usuario=mensaje_usuario,
            numero_nora=numero_nora_real,
            historial=historial
        )

        if not respuesta:
            return {"message": "No se pudo generar una respuesta"}, 200

        try:
            enviar_mensaje_twilio(telefono_usuario, respuesta, numero_nora_real)
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
