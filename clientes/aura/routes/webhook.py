# clientes/aura/routes/webhook.py

import os
from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.supabase import supabase
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 📨 Datos crudos del webhook
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)

        # 📞 Obtener número del remitente
        numero_remitente = normalizar_numero(data.get("To", ""))
        print(f"📞 Número de Nora detectado: {numero_remitente}")

        # 🔍 Buscar la configuración del bot por número_nora
        config_res = (
            supabase.table("configuracion_bot")
            .select("nombre_nora")
            .eq("numero_nora", numero_remitente)
            .execute()
        )
        config_data = config_res.data or []

        if config_data:
            nombre_nora_detectado = config_data[0]["nombre_nora"]
            print(f"🎯 Detectado nombre_nora automáticamente: {nombre_nora_detectado}")
            data["NombreNora"] = nombre_nora_detectado  # 🔧 Reemplazar en los datos
        else:
            print("⚠️ No se detectó configuración válida. Usando 'nora' por defecto.")
            data["NombreNora"] = "nora"

        print(f"🎯 NombreNora validado: '{data['NombreNora']}'")

        # 🤖 Procesar el mensaje
        respuesta = procesar_mensaje(data)

        if not respuesta:
            print("🟡 No se generó una respuesta. Posiblemente sin IA o sin conocimiento.")
        else:
            print(f"✅ Respuesta enviada: {respuesta}")

        return respuesta or "", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
