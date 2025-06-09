# Submódulo de mapeo manual para Meta Ads
import pandas as pd
import os

def filtrar_columnas_mapeables(columnas):
    return [col for col in columnas if col != 'id' and col != 'empresa_id' and not col.endswith('_id') and col != 'subobjetivo']

def obtener_columnas_tabla(supabase, tabla):
    try:
        sql_public = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{tabla}' ORDER BY ordinal_position;"
        resp = supabase.rpc('execute_sql', {'sql': sql_public}).execute()
        if resp.data and len(resp.data) > 0:
            if isinstance(resp.data[0], dict):
                columnas = [row['column_name'] for row in resp.data]
            else:
                columnas = resp.data
            if tabla == 'meta_ads_conjuntos_anuncios':
                columnas = [col for col in columnas if col != 'subobjetivo']
            return columnas
        sql_any = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tabla}' ORDER BY ordinal_position;"
        resp = supabase.rpc('execute_sql', {'sql': sql_any}).execute()
        if resp.data and len(resp.data) > 0:
            if isinstance(resp.data[0], dict):
                columnas = [row['column_name'] for row in resp.data]
            else:
                columnas = resp.data
            if tabla == 'meta_ads_conjuntos_anuncios':
                columnas = [col for col in columnas if col != 'subobjetivo']
            return columnas
    except Exception as e:
        print(f"[ERROR] obtener_columnas_tabla({tabla}): {e}")
    return []

def obtener_columnas_db_dict(supabase):
    campos_campanas = filtrar_columnas_mapeables(obtener_columnas_tabla(supabase, 'meta_ads_campañas'))
    campos_conjuntos = filtrar_columnas_mapeables(obtener_columnas_tabla(supabase, 'meta_ads_conjuntos_anuncios'))
    campos_anuncios = filtrar_columnas_mapeables(obtener_columnas_tabla(supabase, 'meta_ads_anuncios_detalle'))
    return {
        'meta_ads_campañas': campos_campanas,
        'meta_ads_conjuntos_anuncios': campos_conjuntos,
        'meta_ads_anuncios_detalle': campos_anuncios
    }

def obtener_columnas_not_null(supabase, tabla):
    try:
        sql = f"""
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = '{tabla}' AND is_nullable = 'NO' AND column_name != 'id';
        """
        resp = supabase.rpc('execute_sql', {'sql': sql}).execute()
        if resp.data and len(resp.data) > 0:
            if isinstance(resp.data[0], dict):
                cols = [row['column_name'] for row in resp.data]
            else:
                cols = resp.data
            cols = [c.strip().lower() for c in cols]
            return cols
    except Exception as e:
        print(f"[ERROR] obtener_columnas_not_null({tabla}): {e}")
    # Fallback hardcodeado
    if tabla == 'meta_ads_campañas':
        return ['nombre_campaña', 'objetivo', 'entrega', 'fecha_inicio', 'fecha_fin']
    if tabla == 'meta_ads_conjuntos_anuncios':
        return ['nombre_conjunto', 'entrega']
    if tabla == 'meta_ads_anuncios_detalle':
        return ['nombre_anuncio']
    return []

def leer_archivo_temporal(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_json(path)
    except Exception as e:
        print(f"[ERROR] leyendo archivo temporal: {e}")
        return pd.DataFrame()

def generar_preview(df, mapeos_por_tabla, columnas_db_dict, empresa_id):
    columnas_finales = []
    for tabla, cols in columnas_db_dict.items():
        for col_db in cols:
            excel_col = mapeos_por_tabla.get(tabla, {}).get(col_db)
            if excel_col:
                columnas_finales.append((col_db, excel_col))
    datos_finales = []
    for _, row in df.iterrows():
        fila = {}
        for db_col, excel_col in columnas_finales:
            fila[db_col] = row[excel_col] if excel_col in row else None
        fila['empresa_id'] = empresa_id
        datos_finales.append(fila)
    preview = datos_finales[:10]
    columnas = [c[0] for c in columnas_finales]
    return preview, columnas
