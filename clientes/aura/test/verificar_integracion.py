import os
import json

def check_archivo(path, descripcion):
    if not os.path.exists(path):
        print(f"❌ FALTA: {descripcion} → {path}")
        return False
    print(f"✅ OK: {descripcion} → {path}")
    return True

def revisar_bot_data():
    ruta = "clientes/aura/config/bot_data.json"
    if not check_archivo(ruta, "Respuestas automáticas (bot_data.json)"):
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "hola" in data:
            print("✅ Palabra clave 'hola' encontrada en bot_data.json")
        else:
            print("⚠️ No se encontró 'hola' como palabra clave. Nora no podrá saludar.")

    except Exception as e:
        print(f"❌ Error al leer bot_data.json: {e}")

def revisar_conocimiento_txt():
    ruta = "clientes/aura/config/servicios_conocimiento.txt"
    if not check_archivo(ruta, "Archivo de conocimiento para IA"):
        return

    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    if len(contenido) < 20:
        print("⚠️ Archivo de conocimiento cargado pero está muy corto.")
    else:
        print("✅ Contenido de conocimiento cargado correctamente.")

def revisar_settings():
    ruta = "clientes/aura/config/settings.json"
    if not check_archivo(ruta, "Configuración de Nora (settings.json)"):
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            settings = json.load(f)

        for clave in ["usar_ai", "usar_respuestas_automaticas", "usar_manejo_archivos"]:
            estado = settings.get(clave, False)
            print(f"{'✅' if estado else '⚠️'} {clave} → {estado}")

    except Exception as e:
        print(f"❌ Error al leer settings.json: {e}")

if __name__ == "__main__":
    print("🔍 Verificando configuración de Nora...\n")
    revisar_bot_data()
    print()
    revisar_conocimiento_txt()
    print()
    revisar_settings()
