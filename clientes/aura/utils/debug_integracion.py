import os
import json
import openai
from twilio.rest import Client
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

def revisar_todo():
    resultado = "📁 ARCHIVOS Y CONFIGURACIÓN:\n"

    # Verificar archivos esenciales
    base_path = "clientes/aura/config"
    archivos = {
        "settings.json": os.path.join(base_path, "settings.json"),
        "bot_data.json": os.path.join(base_path, "bot_data.json"),
        "servicios_conocimiento.txt": os.path.join(base_path, "servicios_conocimiento.txt"),
    }

    for nombre, ruta in archivos.items():
        if os.path.exists(ruta):
            resultado += f"✅ {nombre} → OK\n"
            if nombre == "bot_data.json":
                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "hola" in data:
                            resultado += "✅ Palabra clave 'hola' encontrada\n"
                        else:
                            resultado += "⚠️ Palabra clave 'hola' NO encontrada\n"
                except Exception as e:
                    resultado += f"❌ Error al leer {nombre}: {e}\n"
        else:
            resultado += f"❌ {nombre} → No encontrado\n"

    # Verificar historial
    historial_dir = "clientes/aura/database/historial"
    if os.path.exists(historial_dir):
        archivos_historial = os.listdir(historial_dir)
        if archivos_historial:
            resultado += f"✅ {len(archivos_historial)} archivos de historial encontrados\n"
        else:
            resultado += f"⚠️ Carpeta de historial vacía\n"
    else:
        resultado += "❌ Carpeta historial → No encontrado (clientes/aura/database/historial)\n"

    # Verificar configuración
    resultado += "\n🧠 CONFIGURACIÓN DE NORA:\n"
    try:
        with open(archivos["settings.json"], "r", encoding="utf-8") as f:
            settings = json.load(f)
            for key in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
                if key in settings:
                    valor = settings[key]
                    resultado += f"✅ {key} → {valor}\n"
                else:
                    resultado += f"❌ Falta la clave '{key}' en settings.json\n"
    except:
        resultado += "❌ No se pudo cargar settings.json\n"

    # Revisar variables de entorno
    resultado += "\n🔐 VARIABLES DE ENTORNO:\n"
    claves_env = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    for clave in claves_env:
        valor = os.getenv(clave)
        if valor:
            resultado += f"✅ {clave} definida\n"
        else:
            resultado += f"❌ {clave} NO definida\n"

    # Validar formato del número de Twilio
    twilio_from = os.getenv("TWILIO_PHONE_NUMBER", "")
    if not twilio_from.startswith("whatsapp:+521"):
        resultado += "❌ TWILIO_PHONE_NUMBER mal formateado (falta el +521...)\n"
        resultado += f"   Valor actual: {twilio_from}\n"
    else:
        resultado += "✅ TWILIO_PHONE_NUMBER con formato correcto (+521...)\n"

    # Comparar con el último 'from' usado
    try:
        with open("clientes/aura/config/twilio_last_sent.json", "r", encoding="utf-8") as f:
            last_data = json.load(f)
            last_from = last_data.get("from", "[no registrado]")
            resultado += f"📤 Último FROM usado: {last_from}\n"

            if last_from != twilio_from:
                resultado += "⚠️ Diferencia entre TWILIO_PHONE_NUMBER y el último FROM utilizado.\n"
    except Exception as e:
        resultado += f"⚠️ No se pudo leer twilio_last_sent.json: {e}\n"

    # Probar conexión OpenAI
    resultado += "\n🔌 CONEXIÓN CON OPENAI:\n"
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        test = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=5
        )
        resultado += "✅ OpenAI respondió correctamente\n"
    except Exception as e:
        resultado += f"❌ Error al conectar con OpenAI: \n\n{e}\n"

    # Probar conexión Twilio
    resultado += "\n📞 CONEXIÓN CON TWILIO:\n"
    try:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(sid, token)
        acc = client.api.accounts(sid).fetch()
        resultado += f"✅ Twilio conectado correctamente\n"
    except Exception as e:
        resultado += f"❌ Error al conectar con Twilio: {e}\n"

    # Probar funciones clave
    resultado += "\n⚙️ FUNCIONES CLAVE DEL BOT:\n"
    try:
        r1 = manejar_respuesta_keywords("hola")
        if r1:
            resultado += f"✅ manejar_respuesta_keywords('hola') devolvió algo\n"
        else:
            resultado += f"⚠️ manejar_respuesta_keywords('hola') devolvió None\n"
    except Exception as e:
        resultado += f"❌ Error en manejar_respuesta_keywords: {e}\n"

    try:
        r2 = manejar_respuesta_ai("¿Qué servicios ofrecen?")
        if r2:
            resultado += f"✅ manejar_respuesta_ai() devolvió respuesta\n"
        else:
            resultado += f"⚠️ manejar_respuesta_ai() no devolvió respuesta\n"
    except Exception as e:
        resultado += f"❌ Error en manejar_respuesta_ai: {e}\n"

    return resultado
