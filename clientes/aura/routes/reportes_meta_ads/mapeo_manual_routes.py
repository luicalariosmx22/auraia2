from . import reportes_meta_ads_bp
from flask import render_template, request, redirect, url_for
from clientes.aura.utils.supabase_client import supabase
from .mapeo_manual import leer_archivo_temporal, obtener_columnas_db_dict, generar_preview
import os
import json

@reportes_meta_ads_bp.route('/reportes/manual/mapeo/confirmar', methods=['GET', 'POST'])
def vista_confirmar_mapeo_manual():
    empresa_id = request.args.get('empresa_id') or request.form.get('empresa_id')
    notas = ''
    feedback = ''
    empresas_db = supabase.table('cliente_empresas').select('*').order('nombre_empresa').execute().data or []
    temp_json_path = f'tmp_reporte_manual_{empresa_id}.json'
    if request.method == 'POST':
        notas = request.form.get('notas', '')
        empresa_id = request.form.get('empresa_id')
        # Guardar prereporte
        if os.path.exists(temp_json_path):
            with open(temp_json_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            prereporte = {
                'id_empresa': empresa_id,
                'notas': notas,
                'datos': datos
            }
            supabase.table('meta_ads_prereportes').insert(prereporte).execute()
            feedback = 'Prerreporte guardado correctamente.'
            # Eliminar archivo temporal si quieres
            os.remove(temp_json_path)
            return render_template('reportes_meta_ads/confirmar_mapeo_manual.html', empresas=empresas_db, empresa_id=empresa_id, feedback=feedback, preview=None, columnas=None, notas=notas)
        else:
            feedback = 'No se encontró el archivo temporal para esta empresa.'
            return render_template('reportes_meta_ads/confirmar_mapeo_manual.html', empresas=empresas_db, empresa_id=empresa_id, feedback=feedback, preview=None, columnas=None, notas=notas)
    # GET: mostrar preview y formulario
    df = leer_archivo_temporal(temp_json_path)
    columnas_db_dict = obtener_columnas_db_dict(supabase)
    # Aquí deberías obtener los mapeos_por_tabla reales del usuario
    mapeos_por_tabla = {}  # <-- Debes cargar los mapeos guardados aquí
    preview, columnas = generar_preview(df, mapeos_por_tabla, columnas_db_dict, empresa_id)
    return render_template('reportes_meta_ads/confirmar_mapeo_manual.html', empresas=empresas_db, empresa_id=empresa_id, feedback=feedback, preview=preview, columnas=columnas, notas=notas)
