import os
import json

def check_archivo(path, descripcion):
    if not os.path.exists(path):
        return f"❌ FALTA: {descripcion} → {path}\n"
    return f"✅ OK: {descripcion} → {path}\n"

def revisar_bot_data():
    ruta = "clientes/aura/config/bot_data.json"
    texto = check_archivo(ruta, "bot_data.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "hola" in data:
            texto += "✅ Palabra clave 'hola' encontrada\n"
        else:
            texto += "⚠️ No se encontró 'hola'\n"
    except Exception as e:
        texto += f"❌ Error al leer bot_data.json: {e}\n"
    return texto

def revisar_conocimiento_txt():
    ruta = "clientes/aura/config/servicios_conocimiento.txt"
    texto = check_archivo(ruta, "Archivo de conocimiento IA")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        if len(contenido) < 20:
            texto += "⚠️ Archivo de conocimiento cargado pero muy corto\n"
        else:
            texto += "✅ Contenido de conocimiento cargado correctamente\n"
    except Exception as e:
        texto += f"❌ Error al leer conocimiento.txt: {e}\n"
    return texto

def revisar_settings():
    ruta = "clientes/aura/config/settings.json"
    texto = check_archivo(ruta, "settings.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            settings = json.load(f)
        for clave in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
            estado = settings.get(clave, False)
            texto += f"{'✅' if estado else '⚠️'} {clave} → {estado}\n"
    except Exception as e:
        texto += f"❌ Error al leer settings.json: {e}\n"
    return texto

def revisar_todo():
    salida = "🔍 Revisión completa:\n\n"
    salida += revisar_bot_data()
    salida += "\n"
    salida += revisar_conocimiento_txt()
    salida += "\n"
    salida += revisar_settings()
    return salida
