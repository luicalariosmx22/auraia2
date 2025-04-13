from flask import Blueprint, request, render_template
import os, json
from clientes.aura.utils.debug_integracion import revisar_todo
from clientes.aura.utils.twilio_sender import enviar_mensaje
from clientes.aura.utils.normalize import normalizar_numero

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug/verificar", methods=["GET"])
def debug_verificacion():
    resultado = revisar_todo()
    return f"<pre>{resultado}</pre>"

@debug_bp.route("/debug/panel", methods=["GET"])
def debug_verificacion_panel():
    return render_template("debug_verificacion.html")

@debug_bp.route("/debug/info", methods=["GET"])
def info_contacto():
    numero = request.args.get("numero")
    if not numero:
        return "⚠️ Debes pasar el número con ?numero=XXXXXXXXXXX"

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

@debug_bp.route("/debug/config", methods=["GET"])
def mostrar_config():
    clave = request.args.get("clave")
    clave_correcta = os.getenv("ADMIN_PASSWORD")

    if clave != clave_correcta:
        return "❌ Acceso denegado. Debes incluir ?clave=ADMIN_PASSWORD"

    claves_a_mostrar = [
        "OPENAI_API_KEY",
        "TWILIO_PHONE_NUMBER",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "LOGIN_PASSWORD"
    ]

    resultado = "🔐 CONFIGURACIÓN ACTUAL (resumen):\n\n"
    for clave_env in claves_a_mostrar:
        valor = os.getenv(clave_env, "[no definido]")
        if "KEY" in clave_env or "TOKEN" in clave_env:
            valor = valor[:6] + "..." if valor != "[no definido]" else valor
        resultado += f"{clave_env}: {valor}\n"

    return f"<pre>{resultado}</pre>"

@debug_bp.route("/debug/twilio-channel-test", methods=["GET"])
def verificar_canal_twilio():
    from twilio.rest import Client

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER", "").replace("whatsapp:", "")

    try:
        client = Client(account_sid, auth_token)
        senders = client.messaging.whatsapp.senders.list()

        salida = f"📡 Canales de WhatsApp en esta cuenta:\n\n"
        encontrado = False

        for sender in senders:
            numero = sender.phone_number
            status = sender.status
            salida += f"• {numero} → Status: {status}\n"

            if from_number in numero:
                encontrado = True

        if not encontrado:
            salida += f"\n❌ Tu número '{from_number}' NO aparece como canal válido."

        return f"<pre>{salida}</pre>"

    except Exception as e:
        return f"❌ Error al consultar los canales de WhatsApp: {e}"

# ✅ Test del normalizador
@debug_bp.route("/debug/test-normalizador", methods=["GET"])
def test_normalizador():
    entrada = request.args.get("n", "+525593372311")
    salida = normalizar_numero(entrada)
    return f"<pre>📞 TEST DEL NORMALIZADOR\nEntrada: {entrada}\nSalida:  {salida}</pre>"
