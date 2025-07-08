from . import reportes_meta_ads_bp
from flask import render_template, request
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.validador_nora import validar_nombre_nora
import pandas as pd
import io
import json
import os
import logging

@reportes_meta_ads_bp.route('/reportes/manual', methods=['GET', 'POST'])
# Vista principal para la carga manual de reportes Meta Ads
# Permite cargar un archivo, previsualizar el mapeo y guardar los datos en la base de datos
# Soporta carga de archivos CSV y Excel
# Utiliza un diccionario de mapeo fijo para traducir columnas del archivo a columnas de la base de datos
# Inserta los datos en las tablas correspondientes de Supabase
# Muestra advertencias si hay columnas no mapeadas o filas no insertadas
# Permite ver y eliminar prereportes guardados

def vista_reporte_manual_meta_ads():
    import sys
    # Diccionario de mapeo fijo: columna del archivo -> (columna_bd, tabla_destino)
    diccionario_mapeo = {
        "Plataforma": ("plataforma", "meta_ads_anuncios_detalle"),
        "Ubicación": ("ubicacion", "meta_ads_anuncios_detalle"),
        "Nombre de la campaña": ("nombre_campaña", "meta_ads_campañas"),
        "Nombre del conjunto de anuncios": ("nombre_conjunto", "meta_ads_conjuntos_anuncios"),
        "Nombre del anuncio": ("nombre_anuncio", "meta_ads_anuncios_detalle"),
        "Nombre de la página": ("pagina", "meta_ads_anuncios_detalle"),
        "Impresiones": ("impresiones", "meta_ads_anuncios_detalle"),
        "Importe gastado (MXN)": ("gasto_mxn", "meta_ads_anuncios_detalle"),
        "Clics en el enlace": ("clics_enlace", "meta_ads_anuncios_detalle"),
        "Costo por resultado": ("costo_resultado", "meta_ads_anuncios_detalle"),
        "Resultados": ("resultados", "meta_ads_anuncios_detalle"),
        "Tipo de resultado": ("tipo_resultado", "meta_ads_anuncios_detalle"),
        "Reproducciones de video": ("reproducciones_video", "meta_ads_anuncios_detalle"),
        "Costo por conversación con mensajes iniciada": ("costo_conversacion", "meta_ads_anuncios_detalle"),
        "Inicio": ("fecha_inicio", "meta_ads_anuncios_detalle"),
        "Finalización": ("fecha_finalizacion", "meta_ads_anuncios_detalle")
    }
    # Si no se recibe nombre_nora, lo obtiene de los argumentos de la vista
    if nombre_nora is None:
        nombre_nora = request.view_args.get('nombre_nora') or request.args.get('nombre_nora')
    # Obtiene la lista de empresas para el selector en el formulario
    empresas_db = supabase.table('cliente_empresas').select('*').order('nombre_empresa').execute().data or []
    empresa_id = None
    if request.method == 'POST':
        # Si se sube un archivo, procesa la carga y genera la previsualización
        if 'archivo_reporte' in request.files:
            archivo = request.files['archivo_reporte']
            import uuid, time
            empresa_id = request.form.get('id_empresa')
            # Si no hay empresa seleccionada, genera un id temporal
            if not empresa_id or empresa_id == '':
                temp_id = str(uuid.uuid4()) + '_' + str(int(time.time()))
                empresa_id = temp_id
            try:
                # Lee el archivo según su extensión
                if archivo.filename.endswith('.csv'):
                    try:
                        df = pd.read_csv(archivo)
                    except Exception as e:
                        feedback = f'Error leyendo archivo CSV: {e}'
                        return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback=feedback), 400
                elif archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                    try:
                        df = pd.read_excel(archivo)
                    except Exception as e:
                        feedback = f'Error leyendo archivo Excel: {e}'
                        return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback=feedback), 400
                else:
                    return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback='Formato de archivo no soportado'), 400
            except Exception as e:
                feedback = f'Error inesperado leyendo archivo: {e}'
                return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback=feedback), 400

            temp_json_path = f'tmp_reporte_manual_{empresa_id}.json'
            try:
                # Agrega la columna empresa_id y guarda el archivo temporal en JSON
                df['empresa_id'] = empresa_id
                df.to_json(temp_json_path, orient='records', force_ascii=False)
            except Exception as e:
                feedback = f'Error guardando archivo temporal: {e}'
                return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback=feedback), 500

            try:
                # Previsualización: mapea las columnas del archivo a las columnas de la base de datos usando el diccionario de mapeo
                columnas_excel = list(df.columns)
                from .mapeo_manual import obtener_columnas_db_dict
                columnas_db_dict = obtener_columnas_db_dict(supabase)
                preview_por_tabla = {k: [] for k in columnas_db_dict.keys()}
                filas_traducidas = 0
                filas_ignoradas = 0
                columnas_diccionario_cmp = {str(col_arch).strip().lower() for col_arch in diccionario_mapeo.keys()}
                columnas_no_mapeadas = set()
                for idx, row in df.iterrows():
                    fila = row.to_dict()
                    fila_mapeada = False
                    for tabla, cols_db in columnas_db_dict.items():
                        fila_traducida = {}
                        for col_archivo, (col_bd, tabla_destino) in diccionario_mapeo.items():
                            if tabla_destino == tabla and col_archivo in fila and col_bd in cols_db:
                                fila_traducida[col_bd] = fila[col_archivo]
                        if fila_traducida:
                            fila_traducida['empresa_id'] = empresa_id
                            preview_por_tabla[tabla].append(fila_traducida)
                            filas_traducidas += 1
                            fila_mapeada = True
                    if not fila_mapeada:
                        filas_ignoradas += 1
                    # Detectar columnas no mapeadas en esta fila
                    fila_keys_cmp = {str(k).strip().lower() for k in fila.keys()}
                    no_mapeadas = fila_keys_cmp - columnas_diccionario_cmp - {'empresa_id'}
                    if no_mapeadas:
                        columnas_no_mapeadas.update(no_mapeadas)
                # Detectar tablas con datos mapeados
                tablas_detectadas = [tabla for tabla, filas in preview_por_tabla.items() if filas]
                prereportes = supabase.table('meta_ads_prereportes').select('*').eq('id_empresa', empresa_id).order('id', desc=True).execute().data or []
                if filas_traducidas == 0:
                    feedback = 'No se pudo mapear ninguna fila del archivo a las tablas destino. Verifica que los nombres de columna del archivo estén en el diccionario.'
                else:
                    feedback = f'Archivo cargado correctamente. Filas mapeadas: {filas_traducidas}. Filas ignoradas: {filas_ignoradas}. Previsualiza los datos y confirma para guardar.'
                    if tablas_detectadas:
                        feedback += f" | Tablas detectadas: {', '.join(tablas_detectadas)}"
                    if columnas_no_mapeadas:
                        feedback += f" | Advertencia: columnas no mapeadas en el diccionario: {', '.join(sorted(columnas_no_mapeadas))}"
                # Renderiza la previsualización de los datos mapeados
                return render_template(
                    'reportes_meta_ads/reporte_manual_meta_ads.html',
                    nombre_nora=nombre_nora,
                    empresas=empresas_db,
                    empresa_id=empresa_id,
                    id_empresa=empresa_id,
                    feedback=feedback,
                    mostrar_previsualizacion=True,
                    columnas_excel=columnas_excel,
                    columnas_db_dict=columnas_db_dict,
                    preview_por_tabla=preview_por_tabla,
                    prereportes=prereportes,
                    preview=None,
                    columnas=None
                )
            except Exception as e:
                feedback = f'Error generando previsualización automática: {e}'
                return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback=feedback), 500
        elif request.form.get('confirmar') == '1':
            # Si el usuario confirma, lee el archivo temporal y realiza el mapeo e inserción en la base de datos
            id_empresa = request.form.get('id_empresa')
            if id_empresa:
                temp_json_path = f'tmp_reporte_manual_{id_empresa}.json'
                if not os.path.exists(temp_json_path):
                    return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback='No se encontró el archivo temporal de datos.'), 400
                with open(temp_json_path, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                from .mapeo_manual import obtener_columnas_db_dict
                columnas_db_dict = obtener_columnas_db_dict(supabase)
                datos_traducidos_por_tabla = {k: [] for k in columnas_db_dict.keys()}
                filas_no_asignadas = 0
                columnas_no_mapeadas = set()
                for idx, fila in enumerate(datos):
                    asignado = False
                    fila_keys_cmp = {str(k).strip().lower() for k in fila.keys()}
                    fila_por_tabla = {k: {} for k in columnas_db_dict.keys()}
                    # Mapea cada columna del archivo a la columna y tabla destino según el diccionario fijo
                    for col_archivo, (col_bd, tabla_destino) in diccionario_mapeo.items():
                        col_archivo_cmp = str(col_archivo).strip().lower()
                        if col_archivo_cmp in fila_keys_cmp and col_bd in columnas_db_dict.get(tabla_destino, []):
                            key_real = next((k for k in fila.keys() if str(k).strip().lower() == col_archivo_cmp), None)
                            if key_real:
                                fila_por_tabla[tabla_destino][col_bd] = fila[key_real]
                    for tabla, fila_traducida in fila_por_tabla.items():
                        if fila_traducida:
                            fila_traducida['empresa_id'] = id_empresa
                            datos_traducidos_por_tabla[tabla].append(fila_traducida)
                            asignado = True
                    if not asignado:
                        filas_no_asignadas += 1
                # Detecta columnas del archivo que no están en el diccionario de mapeo
                columnas_diccionario_cmp = {str(col_arch).strip().lower() for col_arch in diccionario_mapeo.keys()}
                for fila in datos:
                    fila_keys_cmp = {str(k).strip().lower() for k in fila.keys()}
                    no_mapeadas = fila_keys_cmp - columnas_diccionario_cmp - {'empresa_id'}
                    if no_mapeadas:
                        columnas_no_mapeadas.update(no_mapeadas)
                # Inserta los datos mapeados en las tablas correspondientes de Supabase
                datos_preview = {tabla: filas[:2] for tabla, filas in datos_traducidos_por_tabla.items()}
                errores = []
                filas_insertadas = 0
                if datos_traducidos_por_tabla['meta_ads_campañas']:
                    resp_camp = supabase.table('meta_ads_campañas').insert(datos_traducidos_por_tabla['meta_ads_campañas']).execute()
                    if hasattr(resp_camp, 'error') and resp_camp.error:
                        errores.append(f"meta_ads_campañas: {resp_camp.error}")
                    elif hasattr(resp_camp, 'data') and resp_camp.data:
                        filas_insertadas += len(resp_camp.data)
                if datos_traducidos_por_tabla['meta_ads_conjuntos_anuncios']:
                    resp_conj = supabase.table('meta_ads_conjuntos_anuncios').insert(datos_traducidos_por_tabla['meta_ads_conjuntos_anuncios']).execute()
                    if hasattr(resp_conj, 'error') and resp_conj.error:
                        errores.append(f"meta_ads_conjuntos_anuncios: {resp_conj.error}")
                    elif hasattr(resp_conj, 'data') and resp_conj.data:
                        filas_insertadas += len(resp_conj.data)
                if datos_traducidos_por_tabla['meta_ads_anuncios_detalle']:
                    resp_anun = supabase.table('meta_ads_anuncios_detalle').insert(datos_traducidos_por_tabla['meta_ads_anuncios_detalle']).execute()
                    if hasattr(resp_anun, 'error') and resp_anun.error:
                        errores.append(f"meta_ads_anuncios_detalle: {resp_anun.error}")
                    elif hasattr(resp_anun, 'data') and resp_anun.data:
                        filas_insertadas += len(resp_anun.data)
                try:
                    os.remove(temp_json_path)
                except Exception:
                    pass
                prereportes = supabase.table('meta_ads_prereportes').select('*').eq('id_empresa', id_empresa).order('id', desc=True).execute().data or []
                # Genera feedback para el usuario según el resultado de la inserción
                if errores:
                    feedback = 'Ocurrieron errores al guardar en la base de datos: ' + '; '.join(errores)
                elif filas_insertadas == 0:
                    feedback = 'No se insertó ningún dato en las tablas. Verifica que los datos sean válidos, que no estén duplicados y que cumplan los requisitos de la base.'
                else:
                    feedback = f'Datos guardados correctamente en las tablas. Filas insertadas: {filas_insertadas}'
                if columnas_no_mapeadas:
                    feedback += f" | Advertencia: columnas no mapeadas en el diccionario: {', '.join(sorted(columnas_no_mapeadas))}"
                return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback=feedback, prereportes=prereportes, empresa_id=id_empresa)
            else:
                return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, feedback='No se recibió empresa para guardar.'), 400
    # Si es GET o no hay acción, muestra el formulario inicial o la previsualización si hay archivo temporal
    prereportes = []
    if request.method == 'GET' and request.args.get('id_empresa'):
        empresa_id = request.args.get('id_empresa')
        prereportes = supabase.table('meta_ads_prereportes').select('*').eq('id_empresa', empresa_id).order('id', desc=True).execute().data or []
        temp_json_path = f'tmp_reporte_manual_{empresa_id}.json'
        if os.path.exists(temp_json_path):
            with open(temp_json_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            def filtrar_columnas_mapeables(columnas):
                return [col for col in columnas if col != 'id' and col != 'empresa_id' and not col.endswith('_id') and col != 'subobjetivo']
            campos_campanas = filtrar_columnas_mapeables(obtener_columnas_tabla('meta_ads_campañas'))
            campos_conjuntos = filtrar_columnas_mapeables(obtener_columnas_tabla('meta_ads_conjuntos_anuncios'))
            campos_anuncios = filtrar_columnas_mapeables(obtener_columnas_tabla('meta_ads_anuncios_detalle'))
            columnas_db_dict = {
                'meta_ads_campañas': campos_campanas,
                'meta_ads_conjuntos_anuncios': campos_conjuntos,
                'meta_ads_anuncios_detalle': campos_anuncios
            }
            columnas_excel = list(datos[0].keys()) if datos else []
            feedback = 'Se detectó un archivo cargado previamente. Relaciona las columnas y continúa.'
            supabase.table('meta_ads_mapeos_usuario').delete().eq('tabla_destino', 'meta_ads_campañas').execute()
            supabase.table('meta_ads_mapeos_usuario').delete().eq('tabla_destino', 'meta_ads_conjuntos_anuncios').execute()
            supabase.table('meta_ads_mapeos_usuario').delete().eq('tabla_destino', 'meta_ads_anuncios_detalle').execute()
            return render_template(
                'reportes_meta_ads/reporte_manual_meta_ads.html',
                nombre_nora=nombre_nora,
                empresas=empresas_db,
                columnas_db_dict=columnas_db_dict,
                columnas_excel=columnas_excel,
                empresa_id=empresa_id,
                id_empresa=empresa_id,
                feedback=feedback,
                mostrar_mapeo=True,
                mapeos_guardados={},
                prereportes=prereportes
            )
    return render_template('reportes_meta_ads/reporte_manual_meta_ads.html', nombre_nora=nombre_nora, empresas=empresas_db, prereportes=prereportes, empresa_id=empresa_id)

@reportes_meta_ads_bp.route('/reportes/manual/prereportes', methods=['GET'])
def vista_prereportes_guardados(nombre_nora=None):
    try:
        empresa_id = request.args.get('empresa_id')
        prereportes = []
        empresas_db = []
        if empresa_id:
            prereportes = supabase.table('meta_ads_prereportes').select('*').eq('id_empresa', empresa_id).order('id', desc=True).execute().data or []
            empresas_db = supabase.table('cliente_empresas').select('*').eq('id', empresa_id).order('nombre_empresa').execute().data or []
        else:
            prereportes = supabase.table('meta_ads_prereportes').select('*').order('id', desc=True).execute().data or []
            empresas_db = supabase.table('cliente_empresas').select('*').order('nombre_empresa').execute().data or []
        return render_template('reportes_meta_ads/prereportes_guardados.html', prereportes=prereportes, empresas=empresas_db, empresa_id=empresa_id, nombre_nora=nombre_nora)
    except Exception as e:
        return "Error interno en la vista de prereportes", 500

@reportes_meta_ads_bp.route('/reportes/manual/prereportes/eliminar', methods=['POST'])
def eliminar_prereporte(nombre_nora=None):
    try:
        prereporte_id = request.json.get('id') if request.is_json else request.form.get('id')
        if not prereporte_id:
            return {'ok': False, 'msg': 'ID no recibido'}, 400
        supabase.table('meta_ads_prereportes').delete().eq('id', prereporte_id).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'msg': str(e)}, 500

def obtener_columnas_tabla(tabla):
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
        pass
    return []
