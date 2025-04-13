# 📁 Archivo: clientes/aura/utils/startup_check.py

import os
import json

def asegurar_directorio(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"🛠️ Carpeta creada: {path}")
    else:
        print(f"✅ Carpeta existente: {path}")

def asegurar_archivo_json(path, contenido_inicial):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contenido_inicial, f, indent=2, ensure_ascii=False)
        print(f"📄 Archivo creado: {path}")
    else:
        print(f"✅ Archivo existente: {path}")

def verificar_entorno():
    claves = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    for clave in claves:
        if not os.getenv(clave):
            print(f"⚠️ Falta variable de entorno: {clave}")
        else:
            print(f"🔐 {clave} configurada")

def inicializar_nora():
    print("🧩 Iniciando verificación de entorno y estructura para Nora AI...")

    # Carpetas necesarias
    asegurar_directorio("clientes/aura/database/historial")
    asegurar_directorio("clientes/aura/config")

    # Archivos necesarios
    asegurar_archivo_json("clientes/aura/database/logs_errores.json", [])
    verificar_entorno()

    print("✅ Inicialización completa.")

# Llamar esta función desde app.py o manualmente si se desea
if __name__ == "__main__":
    inicializar_nora()