# ✅ Archivo: generar_refresh_token.py
# 👉 Script para obtener refresh_token de Google Ads

import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Configura tus datos aquí (puedes usar os.getenv si prefieres leer desde .env.local)
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "TU_GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "TU_GOOGLE_CLIENT_SECRET")

SCOPES = ["https://www.googleapis.com/auth/adwords"]

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=SCOPES,
)

credentials = flow.run_local_server(port=8080, prompt="consent")

print("\n✅ REFRESH TOKEN:")
print(credentials.refresh_token)
