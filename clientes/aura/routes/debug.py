from flask import Blueprint, request, render_template
from clientes.aura.utils.debug_integracion import revisar_todo
from clientes.aura.utils.twilio_sender import enviar_mensaje
import os
import json

debug_bp = Blueprint("debug", __name__)

# Verificación en formato texto
@debug_bp.route("/debug/verificar", methods=["GET"])
def debug_verificacion():
    resultado = revisar_todo()
    return f"<pre>{resultado}</pre>"

# Verificación visual
@debug_bp.route("/debug/panel", methods=["GET"])
def debug_verificacion_panel():
    return render_template("debug_verificacion.html")

# Ver historial por número
@debug_bp.route("/debug/info", methods=["GET"])
def info_contacto():
    numero = request.args.get("numero")
    if not numero:
        return "⚠️ Debes proporcionar un número con ?numero=XXXXXXXXXXX"

    archivo = f"clientes/aura/database/historial/{numero}.json"
    if not os.path.exists(archivo):
        return f"❌ No hay historial para {numero}"

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            historial = json.load(f)
        ultimos = historial[-5:]
        salida = f"🧾 Últimos mensajes de {numero}:\n\n"
        for m in ultimos:
            salida += f"[{m['hora']}] {m['origen']}: {m['mensaje']}\n"
        return f"<pre>{salida}</pre>"
    except Exception as e:
        return f"❌ Error al leer historial: {e}"

# Borrar historial por número
@debug_bp.route("/debug/reset/historial", methods=["GET"])
def reset_historial():
    numero = request.args.get("numero")
    if not numero:
        return "⚠️ Agrega el número con ?numero=XXXXXXXXXXX"

    archivo = f"clientes/aura/database/historial/{numero}.json"
    if os.path.exists(archivo):
        os.remove(archivo)
        return f"✅ Historial de {numero} eliminado."
    return f"❌ No se encontró historial para {numero}"

# Prueba de envío real por Twilio
@debug_bp.route("/debug/enviar-prueba", methods=["GET"])
def enviar_prueba():
    numero = request.args.get("to")
    if not numero:
        return "❌ Agrega el número con ?to=521XXXXXXXXXX (sin whatsapp:)"

    mensaje = "🧪 Esta es una prueba enviada por Nora desde Twilio (modo producción)"
    sid = enviar_mensaje(numero, mensaje, nombre_contacto="Prueba Debug")

    if sid:
        return f"✅ Mensaje enviado correctamente a {numero}\nSID: {sid}"
    else:
        return f"❌ Error: El mensaje no se pudo enviar a {numero}. Revisa logs en Railway."
