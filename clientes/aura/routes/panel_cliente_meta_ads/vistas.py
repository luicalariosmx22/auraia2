from flask import render_template, jsonify
from . import panel_cliente_meta_ads_bp
from clientes.aura.utils.supabase_client import supabase

@panel_cliente_meta_ads_bp.route('/reportes/reporte/<uuid>', methods=['GET'])
def ver_reporte_meta_ads(uuid):
    """Vista de detalle de un reporte de Meta Ads"""
    try:
        reporte = supabase.table('meta_ads_reportes_semanales')\
            .select('*')\
            .eq('id', uuid)\
            .single()\
            .execute()\
            .data

        print("Datos del reporte:", reporte)  # Para debug

        if not reporte:
            return jsonify({
                'error': 'Reporte no encontrado'
            }), 404

        return render_template('panel_cliente_meta_ads/detalle_reporte.html', 
                            reporte=reporte)

    except Exception as e:
        print(f"Error al obtener reporte: {e}")
        return jsonify({
            'error': f'Error al obtener reporte: {str(e)}'
        }), 500

@panel_cliente_meta_ads_bp.route("/dashboard", methods=["GET"])
def vista_meta_ads():
    """
    Vista del dashboard de Meta Ads.
    """
    try:
        # Obtener estadísticas básicas
        stats = {
            "total_reportes": supabase.table("meta_ads_reportes_semanales").select("count").execute().count,
            "ultima_actualizacion": supabase.table("meta_ads_reportes_semanales")
                .select("created_at")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
                .data[0]["created_at"] if supabase.table("meta_ads_reportes_semanales").select("count").execute().count > 0 else None
        }
        
        return render_template(
            "panel_cliente_meta_ads/dashboard.html",
            stats=stats,
            titulo="Dashboard Meta Ads"
        )
        
    except Exception as e:
        print(f"❌ Error en vista principal Meta Ads: {e}")
        return render_template(
            "panel_cliente_meta_ads/index.html",
            error=f"Error al cargar datos: {str(e)}",
            titulo="Dashboard Meta Ads"
        )
