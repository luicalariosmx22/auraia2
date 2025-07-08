# ✅ Archivo: subir_reporte_anuncios.py

import pandas as pd
from supabase import create_client
import os

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cargar CSV y preparar encabezados
file_path = "Preview_-_Informe_de_Anuncios.csv"
df_raw = pd.read_csv(file_path, header=None)
df_raw.columns = df_raw.iloc[1]
df = df_raw.drop([0, 1]).reset_index(drop=True)

# Reemplazar NaNs por None
df = df.where(pd.notnull(df), None)

# Renombrar columnas para coincidir con la tabla
column_map = {
    "Estado del anuncio": "estado_anuncio",
    "URL final": "url_final",
    "Título 1": "titulo_1",
    "Posición del título 1": "pos_titulo_1",
    "Título 2": "titulo_2",
    "Posición del título 2": "pos_titulo_2",
    "Título 3": "titulo_3",
    "Posición del título 3": "pos_titulo_3",
    "Título 4": "titulo_4",
    "Posición del título 4": "pos_titulo_4",
    "Título 5": "titulo_5",
    "Posición del título 5": "pos_titulo_5",
    "Título 6": "titulo_6",
    "Posición del título 6": "pos_titulo_6",
    "Título 7": "titulo_7",
    "Posición del título 7": "pos_titulo_7",
    "Título 8": "titulo_8",
    "Posición del título 8": "pos_titulo_8",
    "Título 9": "titulo_9",
    "Posición del título 9": "pos_titulo_9",
    "Título 10": "titulo_10",
    "Posición del título 10": "pos_titulo_10",
    "Título 11": "titulo_11",
    "Posición del título 11": "pos_titulo_11",
    "Título 12": "titulo_12",
    "Posición del título 12": "pos_titulo_12",
    "Título 13": "titulo_13",
    "Posición del título 13": "pos_titulo_13",
    "Título 14": "titulo_14",
    "Posición del título 14": "pos_titulo_14",
    "Título 15": "titulo_15",
    "Posición del título 15": "pos_titulo_15",
    "Descripción 1": "descripcion_1",
    "Posición de la descripción 1": "pos_desc_1",
    "Descripción 2": "descripcion_2",
    "Posición de la descripción 2": "pos_desc_2",
    "Descripción 3": "descripcion_3",
    "Posición de la descripción 3": "pos_desc_3",
    "Descripción 4": "descripcion_4",
    "Posición de la descripción 4": "pos_desc_4",
    "Ruta 1": "ruta_1",
    "Ruta 2": "ruta_2",
    "URL final para celulares": "url_final_movil",
    "Plantilla de seguimiento": "plantilla_seguimiento",
    "Sufijo de la URL final": "sufijo_url_final",
    "Parámetro personalizado": "param_personalizado",
    "Campaña": "campaña",
    "Grupo de anuncios": "grupo_anuncios",
    "Estado": "estado",
    "Motivos del estado": "motivos_estado",
    "Calidad del anuncio": "calidad_anuncio",
    "Mejoras en la efectividad del anuncio": "mejoras_efectividad",
    "Tipo de anuncio": "tipo_anuncio",
    "Clics": "clics",
    "Impr.": "impresiones",
    "CTR": "ctr",
    "Código de moneda": "codigo_moneda",
    "Prom. CPC": "cpc_promedio",
    "Costo": "costo",
    "Porcentaje de conv.": "porcentaje_conversion",
    "Conversiones": "conversiones",
    "Costo/conv.": "costo_por_conversion"
}
df = df.rename(columns=column_map)

# Insertar en Supabase
data = df.to_dict(orient="records")
for batch in [data[i:i+100] for i in range(0, len(data), 100)]:
    res = supabase.table("google_ads_reporte_anuncios").insert(batch).execute()
    print(res)

print("✅ Reporte de anuncios cargado a Supabase.")
