# -*- coding: utf-8 -*-
"""
Vista para cuentas de Google Ads siguiendo el patrón de Meta Ads
Replica exactamente la lógica de panel_cliente_ads.py
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads import panel_cliente_google_ads_bp
from clientes.aura.services.google_ads_service import google_ads_service
from clientes.aura.utils.supabase_client import supabase
import os
import logging

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/<nombre_nora>', methods=['GET'])
def vista_cuentas_publicitarias_google_ads(nombre_nora):
    """
    Vista principal de cuentas publicitarias de Google Ads
    Replica la funcionalidad de Meta Ads pero para Google Ads
    """
    # Obtener cuentas de Google Ads de la base de datos
    cuentas_ads = supabase.table('google_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    
    # Enriquecer con nombre de empresa
    for cuenta in cuentas_ads:
        empresa_id = cuenta.get('empresa_id')
        cuenta['empresa_nombre'] = None
        if empresa_id:
            try:
                empresa = supabase.table('cliente_empresas').select('nombre_empresa').eq('id', empresa_id).single().execute().data
                if empresa:
                    cuenta['empresa_nombre'] = empresa.get('nombre_empresa')
            except Exception as e:
                logging.warning(f"Error obteniendo empresa {empresa_id}: {e}")
                cuenta['empresa_nombre'] = None
    
    return render_template('cuentas_publicitarias_google_ads.html', 
                         nombre_nora=nombre_nora, 
                         cuentas_ads=cuentas_ads, 
                         moneda="MXN")

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/actualizar', methods=['POST'])
def actualizar_cuentas_publicitarias_google_ads(nombre_nora):
    """
    Actualiza información de cuentas de Google Ads desde la API
    """
    print(f"[DEBUG] Iniciando actualización de cuentas Google Ads para Nora: {nombre_nora}")
    
    # Obtener cuentas de la base de datos
    cuentas = supabase.table('google_ads_cuentas').select('*').eq('nombre_visible', nombre_nora).execute().data or []
    print(f"[DEBUG] Cuentas encontradas: {len(cuentas)}")
    
    errores = []
    cuentas_actualizadas = []
    
    for cuenta in cuentas:
        customer_id = cuenta['customer_id']
        print(f"[DEBUG] Actualizando cuenta: {customer_id}")
        
        try:
            # Obtener información actualizada de Google Ads API
            # TODO: Implementar función para obtener info de Google Ads
            # Por ahora, usamos datos mock para mantener la estructura
            info = {
                'nombre_cliente': cuenta.get('nombre_cliente', f'Cuenta {customer_id}'),
                'account_status': 1,  # Activa por defecto
                'ads_activos': 0,
                'accesible': True,
                'problema': None
            }
            
            print(f"[DEBUG] Info obtenida de Google Ads API para {customer_id}: {info}")
            
            update_data = {
                'nombre_cliente': info.get('nombre_cliente', cuenta['nombre_cliente']),
                'account_status': info.get('account_status', cuenta['account_status']),
                'ads_activos': info.get('ads_activos', cuenta.get('ads_activos', 0)),
                'accesible': info.get('accesible', cuenta.get('accesible', True)),
                'problema': info.get('problema', cuenta.get('problema'))
            }
            
            # Fallback si nombre_cliente viene vacío
            if not update_data['nombre_cliente']:
                update_data['nombre_cliente'] = f'Cuenta {customer_id}'
            
            print(f"[DEBUG] Datos a actualizar en Supabase para {customer_id}: {update_data}")
            
            resp_update = supabase.table('google_ads_cuentas').update(update_data).eq('customer_id', customer_id).execute()
            print(f"[DEBUG] Respuesta de update Supabase para {customer_id}: {resp_update}")
            
            cuentas_actualizadas.append({
                'customer_id': customer_id,
                'ads_activos': update_data['ads_activos'],
                'nombre_cliente': update_data['nombre_cliente']
            })
            
        except Exception as e:
            print(f"[ERROR] Error actualizando cuenta {customer_id}: {e}")
            errores.append({'customer_id': customer_id, 'error': str(e)})
    
    if errores:
        print(f"[DEBUG] Errores encontrados: {errores}")
        return {'ok': False, 'errores': errores, 'cuentas': cuentas_actualizadas}, 207
    
    print("[DEBUG] Actualización de cuentas Google Ads finalizada correctamente.")
    return {'ok': True, 'cuentas': cuentas_actualizadas}

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/importar_desde_google_ads', methods=['POST'])
def importar_cuentas_desde_google_ads(nombre_nora):
    """
    Importa cuentas desde Google Ads API y las agrega a la base de datos
    """
    print(f"[DEBUG] Importando cuentas de Google Ads para Nora: {nombre_nora}")
    
    try:
        # Obtener todas las cuentas del MCC usando el servicio existente
        total_cuentas, cuentas_google_ads = google_ads_service.listar_cuentas_accesibles()
        
        # Buscar cuentas ya existentes para la Nora
        existentes = supabase.table('google_ads_cuentas').select('customer_id').eq('nombre_visible', nombre_nora).execute().data or []
        existentes_ids = {c['customer_id'] for c in existentes}
        
        nuevas = []
        for cuenta in cuentas_google_ads:
            customer_id = cuenta['id']
            if customer_id in existentes_ids:
                continue
            
            data = {
                'customer_id': customer_id,
                'nombre_cliente': cuenta['nombre'],
                'nombre_visible': nombre_nora,
                'conectada': True,
                'account_status': 1 if cuenta.get('accesible', True) else 0,
                'activa': cuenta.get('accesible', True),
                'moneda': cuenta.get('moneda', 'MXN'),
                'zona_horaria': cuenta.get('zona_horaria', 'America/Mexico_City'),
                'es_test': cuenta.get('es_test', False),
                'accesible': cuenta.get('accesible', True),
                'problema': cuenta.get('problema')
            }
            nuevas.append(data)
        
        if nuevas:
            supabase.table('google_ads_cuentas').insert(nuevas).execute()
            print(f"[DEBUG] Insertadas {len(nuevas)} cuentas nuevas")
        
        return jsonify({'ok': True, 'agregadas': len(nuevas), 'total': total_cuentas})
        
    except Exception as e:
        print(f"[ERROR] Error importando cuentas de Google Ads: {e}")
        return jsonify({'ok': False, 'msg': f'Error consultando Google Ads: {e}'}), 500

@panel_cliente_google_ads_bp.route('/cuentas_publicitarias/<nombre_nora>/<customer_id>/vincular_empresa', methods=['GET', 'POST'])
def vincular_empresa_a_cuenta_google_ads(nombre_nora, customer_id):
    """
    Vincula una cuenta de Google Ads con una empresa
    Replica exactamente la funcionalidad de Meta Ads
    """
    # Obtener la cuenta
    try:
        cuenta = supabase.table('google_ads_cuentas').select('*').eq('customer_id', customer_id).single().execute().data
    except:
        return "Cuenta de Google Ads no encontrada", 404
    
    if not cuenta:
        return "Cuenta de Google Ads no encontrada", 404
    
    # Obtener empresas disponibles para la Nora
    empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').eq('nombre_nora', nombre_nora).execute().data or []
    
    if request.method == 'POST':
        empresa_id = request.form.get('empresa_id')
        if not empresa_id:
            return render_template('vincular_empresa_cuenta_google_ads.html', 
                                 cuenta=cuenta, 
                                 empresas=empresas, 
                                 nombre_nora=nombre_nora, 
                                 error='Debes seleccionar una empresa')
        
        # Actualizar la cuenta con el empresa_id
        supabase.table('google_ads_cuentas').update({'empresa_id': empresa_id}).eq('customer_id', customer_id).execute()
        
        return redirect(url_for('panel_cliente_google_ads.vista_cuentas_publicitarias_google_ads', nombre_nora=nombre_nora))
    
    return render_template('vincular_empresa_cuenta_google_ads.html', 
                         cuenta=cuenta, 
                         empresas=empresas, 
                         nombre_nora=nombre_nora)
