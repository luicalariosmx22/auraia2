import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Alcance necesario para trabajar con Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# ID de la hoja de cálculo y el rango que deseas leer o escribir
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")  # Configura el ID de tu hoja en las variables de entorno
RANGE_NAME = 'Sheet1!A1:D10'  # Rango en la hoja (puedes modificarlo)

def get_gsheet_service():
    """
    Autenticarse con la cuenta de servicio y obtener el servicio de Google Sheets.
    """
    try:
        # Validar que las variables de entorno necesarias estén configuradas
        required_env_vars = [
            "GOOGLE_SHEET_CLIENT_ID",
            "GOOGLE_SHEET_CLIENT_SECRET",
            "GOOGLE_SHEET_PROJECT_ID",
            "GOOGLE_SHEET_AUTH_URI",
            "GOOGLE_SHEET_TOKEN_URI",
            "GOOGLE_SHEET_AUTH_PROVIDER_X509_CERT_URL"
        ]
        for var in required_env_vars:
            if not os.getenv(var):
                raise ValueError(f"❌ La variable de entorno {var} no está configurada.")

        # Crear credenciales desde las variables de entorno
        creds = Credentials.from_service_account_info(
            {
                "client_id": os.getenv("GOOGLE_SHEET_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_SHEET_CLIENT_SECRET"),
                "auth_uri": os.getenv("GOOGLE_SHEET_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_SHEET_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_SHEET_AUTH_PROVIDER_X509_CERT_URL"),
                "project_id": os.getenv("GOOGLE_SHEET_PROJECT_ID"),
                "private_key": os.getenv("GOOGLE_SHEET_PRIVATE_KEY").replace("\\n", "\n"),
                "private_key_id": os.getenv("GOOGLE_SHEET_PRIVATE_KEY_ID"),
                "type": "service_account"
            },
            scopes=SCOPES
        )

        # Construir el servicio de Google Sheets
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Error al autenticar con Google Sheets: {e}")
        raise

def read_data():
    """
    Leer datos de la hoja de cálculo.
    """
    try:
        service = get_gsheet_service()
        sheet = service.spreadsheets()

        # Llamar a la API de Sheets para obtener los valores del rango
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('⚠️ No se encontraron datos en la hoja.')
        else:
            print('📄 Datos de la hoja:')
            for row in values:
                print(row)
    except Exception as e:
        print(f"❌ Error al leer datos de Google Sheets: {e}")

def write_data(values):
    """
    Escribir datos en la hoja de cálculo.
    :param values: Lista de listas con los datos a escribir.
    """
    try:
        service = get_gsheet_service()
        sheet = service.spreadsheets()

        # Los valores que se desean escribir
        body = {
            'values': values
        }

        # Realiza la llamada para actualizar el rango de la hoja
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"✅ {result.get('updatedCells')} celdas actualizadas.")
    except Exception as e:
        print(f"❌ Error al escribir datos en Google Sheets: {e}")

# Ejemplo de cómo escribir datos
if __name__ == "__main__":
    values = [
        ["Nombre", "Correo", "Teléfono"],
        ["Juan Pérez", "juanperez@example.com", "5551234567"],
        ["Ana Gómez", "anagomez@example.com", "5559876543"]
    ]
    write_data(values)

    # Para leer datos, puedes usar:
    # read_data()
