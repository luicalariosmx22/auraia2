print("✅ procesar_envios.py cargado correctamente")

import time, json, os, datetime

def leer_contactos():
    with open("clientes/aura/database/contactos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_historial(nombre_nora, numero, mensajes):
    ruta = f"clientes/{nombre_nora}/database/historial/{numero}.json"
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, indent=2, ensure_ascii=False)

def leer_historial(nombre_nora, numero):
    ruta = f"clientes/{nombre_nora}/database/historial/{numero}.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def procesar_envios():
    while True:
        ruta = "clientes/aura/database/envios/envios_programados.json"
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                pendientes = json.load(f)

            nuevos = []
            ahora = datetime.datetime.now()

            for envio in pendientes:
                fecha_hora = datetime.datetime.strptime(f"{envio['fecha']} {envio['hora']}", "%Y-%m-%d %H:%M")
                if fecha_hora <= ahora:
                    print(f"📤 Enviando mensaje programado a {envio['numero']}")
                    historial = leer_historial(envio["nombre_nora"], envio["numero"])
                    historial.append({
                        "origen": "nora",
                        "texto": envio["mensaje"],
                        "hora": ahora.strftime("%H:%M")
                    })

                    contactos = leer_contactos()
                    contacto = next((c for c in contactos if c["numero"] == envio["numero"]), {})

                    if contacto.get("ia_activada"):
                        respuesta = f"Respuesta automática a: {envio['mensaje']}"
                        historial.append({
                            "origen": "nora",
                            "texto": respuesta,
                            "hora": ahora.strftime("%H:%M")
                        })

                    guardar_historial(envio["nombre_nora"], envio["numero"], historial)
                else:
                    nuevos.append(envio)

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(nuevos, f, indent=2, ensure_ascii=False)

        time.sleep(30)

if __name__ == "__main__":
    print("🕒 Procesador de envíos iniciado")
    procesar_envios()
