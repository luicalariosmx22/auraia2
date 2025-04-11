import os
import shutil

# Rutas base
BASE = os.getcwd()
CLIENTE = os.path.join(BASE, "clientes", "aura")

# Carpetas que queremos mover al cliente
carpetas_a_mover = ["handlers", "utils", "routes"]
archivos_a_mover = [
    "config.json", "bot_data.json", "etiquetas.json",
    "historial_conversaciones.json", "logs_errores.json",
    "categorias.json", "contactos_info.json", "Profile"
]

# Crear estructura base si no existe
for carpeta in ["handlers", "utils", "routes", "config", "database"]:
    ruta = os.path.join(CLIENTE, carpeta)
    os.makedirs(ruta, exist_ok=True)

# Mover carpetas
for carpeta in carpetas_a_mover:
    origen = os.path.join(BASE, carpeta)
    destino = os.path.join(CLIENTE, carpeta)
    if os.path.exists(origen):
        print(f"📦 Moviendo carpeta: {carpeta} → {destino}")
        shutil.move(origen, destino)

# Mover archivos
for archivo in archivos_a_mover:
    origen = os.path.join(BASE, archivo)

    if os.path.exists(origen):
        # Si es archivo de configuración
        if archivo.endswith(".json") or archivo.endswith(".env"):
            destino = os.path.join(CLIENTE, "config", archivo)
        else:
            destino = os.path.join(CLIENTE, "database", archivo)

        print(f"📁 Moviendo archivo: {archivo} → {destino}")
        shutil.move(origen, destino)

print("✅ Archivos movidos correctamente a clientes/aura/")
