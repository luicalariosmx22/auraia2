import os
import json
import openai
from twilio.rest import Client
from clientes.aura.handlers.handle_keywords import manejar_respuesta_keywords
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from clientes.aura.utils.normalize import normalizar_numero

def check_archivo(path, descripcion):
    if not os.path.exists(path):
        return f"❌ {descripcion} → No encontrado ({path})\n"
    return f"✅ {descripcion} → OK\n"

def revisar_bot_data():
    ruta = "clientes/aura/config/bot_data.json"
    resultado = check_archivo(ruta, "bot_data.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        if any("hola" in v.get("palabras_clave", []) for v in data.values()):
            resultado += "✅ Palabra clave 'hola' encontrada\n"
        else:
            resultado += "⚠️ 'hola' no está entre las palabras clave\n"
    except Exception as e:
        resultado += f"❌ Error al leer bot_data.json: {e}\n"
    return resultado

def revisar_conocimiento_txt():
    ruta = "clientes/aura/config/servicios_conocimiento.txt"
    resultado = check_archivo(ruta, "Base de conocimiento IA")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        if len(contenido) < 30:
            resultado += "⚠️ Archivo cargado pero demasiado corto\n"
        else:
            resultado += "✅ Contenido de conocimiento cargado correctamente\n"
    except Exception as e:
        resultado += f"❌ Error al leer servicios_conocimiento.txt: {e}\n"
    return resultado

def revisar_settings():
    ruta = "clientes/aura/config/settings.json"
    resultado = check_archivo(ruta, "settings.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            settings = json.load(f)
        for clave in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
            valor = settings.get(clave)
            resultado += f"{'✅' if valor else '⚠️'} {clave} → {valor}\n"
    except Exception as e:
        resultado += f"❌ Error al leer settings.json: {e}\n"
    return resultado

def revisar_variables_entorno():
    claves = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    resultado = "🔐 VARIABLES DE ENTORNO:\n"
    for clave in claves:
        valor = os.getenv(clave)
        resultado += f"{'✅' if valor else '❌'} {clave} {'definida' if valor else 'NO definida'}\n"
    return resultado

def revisar_conexion_openai():
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Prueba de conexión"}],
            temperature=0.0
        )
        if respuesta.choices:
            return "✅ OpenAI respondió correctamente\n"
        return "⚠️ OpenAI respondió vacío\n"
    except Exception as e:
        return f"❌ Error al conectar con OpenAI:\n{e}\n"

def revisar_conexion_twilio():
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        client.api.accounts.list(limit=1)
        return "✅ Twilio conectado correctamente\n"
    except Exception as e:
        return f"❌ Error al conectar con Twilio:\n{e}\n"

def revisar_funciones_clave():
    resultado = "⚙️ FUNCIONES CLAVE DEL BOT:\n"

    try:
        resp1 = manejar_respuesta_keywords("hola")
        if resp1:
            resultado += "✅ manejar_respuesta_keywords('hola') devolvió respuesta\n"
        else:
            resultado += "⚠️ manejar_respuesta_keywords('hola') devolvió None\n"
    except Exception as e:
        resultado += f"❌ Error en manejar_respuesta_keywords: {e}\n"

    try:
        resp2 = manejar_respuesta_ai("¿Qué servicios ofrecen?")
        if resp2:
            resultado += "✅ manejar_respuesta_ai() devolvió respuesta\n"
        else:
            resultado += "⚠️ manejar_respuesta_ai() devolvió None\n"
    except Exception as e:
        resultado += f"❌ Error en manejar_respuesta_ai: {e}\n"

    return resultado

def revisar_historial():
    historial_dir = "clientes/aura/database/historial"
    if not os.path.exists(historial_dir):
        return "❌ Carpeta de historial no encontrada\n"
    archivos = os.listdir(historial_dir)
    if not archivos:
        return "⚠️ Carpeta de historial vacía\n"
    return f"✅ {len(archivos)} archivos de historial encontrados\n"

def revisar_normalizador():
    entrada = "whatsapp:+5216621234567"
    salida = normalizar_numero(entrada)

    if salida != entrada:
        return (
            "📞 NORMALIZADOR DE NÚMEROS:\n"
            f"❌ Error: se perdió el prefijo 'whatsapp:'\n"
            f"Entrada: {entrada}\nSalida: {salida}\n"
        )
    return (
        "📞 NORMALIZADOR DE NÚMEROS:\n"
        f"✅ Entrada: {entrada}\n"
        f"✅ Salida:  {salida}\n"
    )

def revisar_todo():
    salida = ""
    salida += "📁 ARCHIVOS Y CONFIGURACIÓN:\n"
    salida += revisar_settings()
    salida += revisar_bot_data()
    salida += revisar_conocimiento_txt()
    salida += check_archivo("clientes/aura/database/historial", "Carpeta historial")
    salida += "\n"
    salida += "🧠 CONFIGURACIÓN DE NORA:\n"
    salida += revisar_settings()
    salida += "\n"
    salida += revisar_variables_entorno()
    salida += "\n"
    salida += "🔌 CONEXIÓN CON OPENAI:\n"
    salida += revisar_conexion_openai()
    salida += "\n"
    salida += "📞 CONEXIÓN CON TWILIO:\n"
    salida += revisar_conexion_twilio()
    salida += "\n"
    salida += revisar_funciones_clave()
    salida += "\n"
    salida += "🕑 HISTORIAL DE CONVERSACIONES:\n"
    salida += revisar_historial()
    salida += "\n"
    salida += revisar_normalizador()

    return salida
