# 📁 Archivo: clientes/aura/routes/debug_oauthlib.py

import pkg_resources

def verificar_oauthlib():
    try:
        version = pkg_resources.get_distribution("requests-oauthlib").version
        estado = "✅ Correcta" if version.startswith("1.") else f"⚠️ Versión no recomendada ({version})"

        return {
            "version": version,
            "estado": estado
        }
    except Exception as e:
        return {
            "version": None,
            "estado": f"❌ No instalada ({str(e)})"
        }

# DEBUG
print("✅ Módulo debug_oauthlib.py cargado correctamente.")
