import os
import google.auth
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Ruta a tu archivo JSON de la cuenta de servicio
SERVICE_ACCOUNT_FILE = 'credentials/service_account.json'

# Alcance necesario para trabajar con Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# ID de la hoja de cálculo y el rango que deseas leer o escribir
SPREADSHEET_ID = 'TU_ID_DE_HOJA_DE_CÁLCULO'  # Reemplaza con el ID de tu hoja
RANGE_NAME = 'Sheet1!A1:D10'  # Rango en la hoja (puedes modificarlo)

def get_gsheet_service():
    """Autenticarse con la cuenta de servicio y obtener el servicio de Google Sheets"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Guarda el token para futuras autenticaciones
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    return service

def read_data():
    """Leer datos de la hoja de cálculo"""
    service = get_gsheet_service()
    sheet = service.spreadsheets()

    # Llamar a la API de Sheets para obtener los valores del rango
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Data from sheet:')
        for row in values:
            print(row)

def write_data(values):
    """Escribir datos en la hoja de cálculo"""
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
    print(f'{result.get("updatedCells")} cells updated.')

# Ejemplo de cómo escribir datos
values = [
    ["Nombre", "Correo", "Teléfono"],
    ["Juan Pérez", "juanperez@example.com", "5551234567"],
    ["Ana Gómez", "anagomez@example.com", "5559876543"]
]
write_data(values)

# Para leer datos, puedes usar:
# read_data()
