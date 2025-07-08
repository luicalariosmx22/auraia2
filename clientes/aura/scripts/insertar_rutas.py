from clientes.aura.utils.validar_uuid import insertar_datos_con_uuid

# Datos de ejemplo
datos_ruta = {
    "id": "",  # UUID vacío (invalidará el campo)
    "nombre": "Ruta de Prueba",
    "descripcion": "Descripción de la ruta activa"
}

# Insertar datos en la tabla "rutas"
respuesta = insertar_datos_con_uuid("rutas", datos_ruta)

if "error" in respuesta:
    print("❌ Error al insertar ruta:", respuesta["error"])
else:
    print("✅ Ruta insertada correctamente:", respuesta)