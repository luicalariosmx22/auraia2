"""
✅ Script para obtener TODAS las cuentas publicitarias y generar SQL para insertarlas en Supabase.

Instrucciones:
1️⃣ Coloca tu token de usuario abajo.
2️⃣ Corre el script: python fetch_all_adaccounts.py
"""

import requests

# ✅ TU TOKEN AQUÍ
ACCESS_TOKEN = "EAAPJAAprGjgBOwxmmQsIrrM03tDiygBaaJHXEMxLBs1QG5ci5AhVNk01j0UBYZCHL9gIhKkSWVsuKi2k2aQG335tZBOkDVhDBoQO5zZAP3DjvT1RHSKxWynz8vNVVhB0jp1zXo8yTAZBiMfW0Df7PcL2pLGMQHbHLRd582lHvqBrhFFoMLHsybSy6jZCpyH0Pp60JI38lQK2DIIQ2Xhq4iKZC1utzoKgZDZD"

# ✅ TU NOMBRE DE NORA PARA GUARDAR
NOMBRE_NORA = "aura"

def fetch_ad_accounts():
    url = f"https://graph.facebook.com/v19.0/me/adaccounts"
    params = {
        "fields": "id,account_id,name,account_status",
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("data", [])

def generate_sql(accounts):
    sql_lines = []
    for acc in accounts:
        id_publicitaria = acc.get("account_id")
        nombre_cliente = acc.get("name", "").replace("'", "''")  # Escape comillas simples
        status = acc.get("account_status", 0)
        sql = f"""
INSERT INTO meta_ads_cuentas (
    id_cuenta_publicitaria,
    nombre_cliente,
    nombre_visible,
    conectada,
    access_token,
    account_status
) VALUES (
    '{id_publicitaria}',
    '{nombre_cliente}',
    '{NOMBRE_NORA}',
    true,
    '{ACCESS_TOKEN}',
    {status}
);
""".strip()
        sql_lines.append(sql)
    return "\n\n".join(sql_lines)

if __name__ == "__main__":
    cuentas = fetch_ad_accounts()
    if cuentas:
        print(f"✅ {len(cuentas)} cuentas encontradas.\n")
        sql_script = generate_sql(cuentas)
        with open("meta_ads_cuentas_insert.sql", "w") as f:
            f.write(sql_script)
        print("🚀 Archivo 'meta_ads_cuentas_insert.sql' generado correctamente ✅")
    else:
        print("⚠️ No se encontraron cuentas publicitarias o error en el token.")
