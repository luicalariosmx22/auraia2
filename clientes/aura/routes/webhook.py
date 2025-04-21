# 📁 clientes/aura/routes/webhook.py

from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.supabase import supabase
from clientes.aura.utils.normalizador import normalizar_numero

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
            print("⚠️ No se encontró configuración para este número. Usando 'nora' como fallback.")
            data["NombreNora"] = "nora"

        print(f"🎯 NombreNora validado: '{data['NombreNora']}'")

        # 🧠 Procesar el mensaje
        respuesta = procesar_mensaje(data)

        if respuesta:
            print(f"✅ Respuesta enviada: {respuesta}")
        else:
            print("🟡 No se generó una respuesta. Posiblemente sin IA o sin conocimiento.")

        return respuesta or "", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
