import requests

def probar_rutas():
    print("🔍 Probando ruta '/debug/rutas'...")
    try:
        respuesta = requests.get("http://localhost:5000/debug/rutas")
        if respuesta.status_code == 200:
            print("✅ La ruta '/debug/rutas' respondió correctamente.")
        else:
            print(f"❌ Error en '/debug/rutas': {respuesta.status_code}")
    except Exception as e:
        print(f"❌ Excepción al probar '/debug/rutas': {str(e)}")

def probar_verificar():
    print("🔍 Probando ruta '/debug/verificar'...")
    try:
        respuesta = requests.get("http://localhost:5000/debug/verificar")
        if respuesta.status_code == 200:
            print("✅ La ruta '/debug/verificar' respondió correctamente.")
        else:
            print(f"❌ Error en '/debug/verificar': {respuesta.status_code}")
    except Exception as e:
        print(f"❌ Excepción al probar '/debug/verificar': {str(e)}")

def probar_insercion_supabase():
    print("🔍 Probando inserción en Supabase...")
    try:
        from clientes.aura.utils.validar_uuid import insertar_datos_con_uuid

        datos_ruta = {
            "id": "",  # UUID vacío
            "nombre": "Ruta de Prueba",
            "descripcion": "Descripción de la ruta activa"
        }

        respuesta = insertar_datos_con_uuid("rutas", datos_ruta)
        if "error" in respuesta:
            print(f"❌ Error al insertar datos en Supabase: {respuesta['error']}")
        else:
            print("✅ Inserción en Supabase completada exitosamente.")
    except Exception as e:
        print(f"❌ Excepción al probar inserción en Supabase: {str(e)}")

if __name__ == "__main__":
    probar_rutas()
    probar_verificar()
    probar_insercion_supabase()