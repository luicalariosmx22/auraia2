import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local')
load_dotenv(env_path)

def listar_cuentas_publicitarias():
    config = {
        "developer_token": os.getenv("GOOGLE_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_LOGIN_CUSTOMER_ID").replace("-", "") if os.getenv("GOOGLE_LOGIN_CUSTOMER_ID") else None,
        "use_proto_plus": True,
        "transport": "rest"
    }

    print("🔍 CONFIG GOOGLE ADS:")
    for k, v in config.items():
        print(f"{k} = {v}")

    # Verifica que no haya campos faltantes
    for key, val in config.items():
        if val is None:
            raise ValueError(f"❌ Falta la variable de entorno: {key}")

    # No se especifica version para que tome la más reciente disponible
    client = GoogleAdsClient.load_from_dict(config)

    try:
        query = """
            SELECT customer.id, customer.descriptive_name FROM customer
        """
        ga_service = client.get_service("GoogleAdsService")
        response = ga_service.search(customer_id=config["login_customer_id"], query=query)

        cuentas = []
        for row in response:
            cuentas.append({
                "id": row.customer.id,
                "nombre": row.customer.descriptive_name
            })

        return len(cuentas), cuentas

    except Exception as e:
        raise RuntimeError(f"❌ Error al listar cuentas vía REST: {e}")

if __name__ == "__main__":
    listar_cuentas_publicitarias()
