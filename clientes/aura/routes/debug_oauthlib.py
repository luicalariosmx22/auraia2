# clientes/aura/routes/debug_oauthlib.py

import pkg_resources

def verificar_oauthlib():
    try:
        version = pkg_resources.get_distribution("requests-oauthlib").version
        if version.startswith("1."):
            estado = "✅ Correcta"
        else:
            estado = "⚠️ Revisión recomendada"

        return {
            "version": version,
            "estado": estado
        }
    except Exception as e:
        return {
            "version": None,
            "estado": f"❌ No instalada ({str(e)})"
        }
