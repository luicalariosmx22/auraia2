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
        "login_customer_id": os.getenv("GOOGLE_LOGIN_CUSTOMER_ID"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "use_proto_plus": True,
    }

    # Verifica que no haya campos faltantes
    for key, val in config.items():
        if val is None:
            raise ValueError(f"❌ Falta la variable de entorno: {key}")

    try:
        client = GoogleAdsClient.load_from_dict(config, version="v16")
        ga_service = client.get_service("GoogleAdsService")

        query = """
        SELECT customer_client.client_customer,
               customer_client.level,
               customer_client.manager,
               customer_client.descriptive_name,
               customer_client.currency_code,
               customer_client.time_zone,
               customer_client.id
        FROM customer_client
        WHERE customer_client.level <= 1
        """

        response = ga_service.search_stream(customer_id=config["login_customer_id"], query=query)

        cuentas = []
        for batch in response:
            for row in batch.results:
                cuentas.append({
                    "id": row.customer_client.id,
                    "nombre": row.customer_client.descriptive_name,
                    "manager": row.customer_client.manager,
                    "nivel": row.customer_client.level,
                })

        return len(cuentas), cuentas

    except Exception as e:
        print("❌ Error al obtener cuentas:", e)
        raise e

if __name__ == "__main__":
    listar_cuentas_publicitarias()
