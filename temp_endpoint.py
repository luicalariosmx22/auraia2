@webhooks_api_bp.route("/paginas")
def api_paginas_webhook(nombre_nora):
    try:
        # Obtener lista de páginas para el filtro
        paginas = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina") \
            .eq("activa", True) \
            .order("nombre_pagina") \
            .execute()
        return jsonify({'success': True, 'paginas': paginas.data or []})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
