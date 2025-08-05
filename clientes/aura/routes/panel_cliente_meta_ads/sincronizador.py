from flask import Blueprint, request, redirect, url_for, flash, jsonify
from clientes.aura.routes.panel_cliente_meta_ads.sincronizador_semanal import sincronizar_reportes_semanales

from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp

@panel_cliente_meta_ads_bp.route("/sincronizar-semanal", methods=["GET"])
def vista_sincronizacion_semanal(nombre_nora):
    try:
        print(f"🚀 Iniciando sincronización para: {nombre_nora}")
        resultado = sincronizar_reportes_semanales(nombre_nora)
        
        if isinstance(resultado, int):
            if resultado > 0:
                return jsonify({
                    'ok': True,
                    'message': f'Reporte semanal generado correctamente. {resultado} reportes creados.',
                    'reportes_generados': resultado
                })
            else:
                # Verificar si ya existen reportes para mostrar mensaje apropiado
                from clientes.aura.utils.supabase_client import supabase
                reportes_existentes = supabase.table('meta_ads_reportes_semanales')\
                    .select('id')\
                    .eq('nombre_nora', nombre_nora)\
                    .gte('fecha_inicio', '2025-07-28')\
                    .lte('fecha_fin', '2025-08-04')\
                    .execute()
                
                if reportes_existentes.data:
                    return jsonify({
                        'ok': True,
                        'message': f'Los reportes ya existen para esta semana. Se encontraron {len(reportes_existentes.data)} reportes.',
                        'reportes_existentes': len(reportes_existentes.data)
                    })
                else:
                    return jsonify({
                        'ok': False,
                        'error': 'No se pudieron generar reportes. Verifica que haya datos disponibles.'
                    }), 400
        elif isinstance(resultado, dict) and resultado.get('success'):
            return jsonify({
                'ok': True,
                'message': 'Reporte semanal generado correctamente',
                'data': resultado
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'No se pudieron generar reportes. Verifica que haya datos disponibles.'
            }), 400
            
    except Exception as e:
        print(f"❌ Error en vista_sincronizacion_semanal: {str(e)}")
        return jsonify({
            'ok': False,
            'error': f'Error al generar el reporte: {str(e)}'
        }), 500
