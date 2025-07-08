"""
Script para sincronizar las columnas de campañas entre los dos generadores
y agregar las columnas faltantes que están causando el error
"""

def get_google_ads_generator_campaigns_columns():
    """Columnas de campañas del generador de IA (google_ads_sql_generator.py)"""
    return [
        'estado_campaña', 'campaña', 'presupuesto', 'nombre_presupuesto', 'tipo_presupuesto',
        'estado', 'motivos_estado', 'tipo_campaña', 'impresiones', 'ctr', 'codigo_moneda',
        'costo', 'anuncios_aptos', 'anuncios_rechazados', 'palabras_clave_aptas',
        'palabras_clave_rechazadas', 'grupos_anuncios_aptos', 'anuncios_responsivos_aptos',
        'calidad_anuncio', 'vinculos_aptos_heredados', 'vinculos_aptos_actualizados',
        'imagenes_aptas_heredadas', 'imagenes_aptas_actualizadas', 'resultados',
        'valor_resultados', 'cliente_potencial_llamada', 'conversiones', 'costo_conversion',
        'porcentaje_conversion', 'valor_conversion', 'conversiones_vista', 'costo_conversion_vista',
        'valor_conversion_vista', 'todas_conversiones', 'costo_todas_conversiones',
        'valor_todas_conversiones', 'conversion_cruzada_dispositivo', 'clics', 'cpc_promedio',
        'cpm_promedio', 'participacion_impresiones_busqueda', 'participacion_impresiones_display',
        'tasa_impresiones_perdidas_ranking', 'tasa_impresiones_perdidas_presupuesto',
        'calidad_optimizacion', 'interacciones', 'tasa_interaccion', 'costo_interaccion',
        'video_vistas', 'vista_25', 'vista_50', 'vista_75', 'vista_100', 'clics_llamada_telefono',
        'impresiones_llamada_telefono', 'ctr_llamada_telefono', 'descarga_aplicacion_promocionada',
        'instalaciones_aplicacion_promocionada', 'instalaciones_aplicacion_promocionada_vista',
        'compras_aplicacion_promocionada', 'compras_aplicacion_promocionada_vista',
        'costo_compra_aplicacion_promocionada', 'ingresos_compra_aplicacion_promocionada',
        'registros_aplicacion_promocionada', 'registros_aplicacion_promocionada_vista',
        'costo_registro_aplicacion_promocionada', 'valor_registro_aplicacion_promocionada',
        'compras_con_seguimiento', 'valor_compras_con_seguimiento', 'compras_con_seguimiento_vista',
        'valor_compras_con_seguimiento_vista', 'costo_compra_con_seguimiento',
        'reservas_hoteles_promocionados', 'impresiones_local_promocionado', 'acciones_local_promocionado',
        'valor_acciones_local_promocionado', 'costo_accion_local_promocionado',
        'direcciones_local_promocionado', 'llamadas_telefono_local_promocionado',
        'visitas_tienda_local_promocionado', 'visitas_menu_local_promocionado',
        'pedidos_local_promocionado', 'reservas_local_promocionado', 'gmail_aperturas',
        'gmail_guardados', 'gmail_reenvios', 'gmail_clics_llamada', 'participaciones_sociales',
        'clic_sitio_web', 'me_gusta_pagina', 'me_gusta_publicacion', 'comentarios_publicacion',
        'shares_publicacion', 'suscripciones_canal', 'vistas_perfil_empresa',
        'llamadas_desde_anuncios', 'revenue_hotel_ads', 'eligible_impressions_local',
        'location_clicks', 'phone_calls', 'phone_impressions', 'store_visits',
        'website_clicks', 'absolute_top_impression_share', 'click_assisted_conversions',
        'click_assisted_conversion_value', 'cost_per_conversion_from_location_extension',
        'cross_device_conversions', 'historical_creative_quality_score',
        'historical_landing_page_quality_score', 'historical_quality_score',
        'historical_search_predicted_ctr', 'impression_assisted_conversions',
        'impression_assisted_conversion_value', 'interaction_event_types',
        'invalid_click_rate', 'invalid_clicks', 'message_chats', 'message_impressions',
        'optimization_score', 'phone_through_rate', 'relative_ctr', 'search_absolute_top_impression_share',
        'search_budget_lost_impression_share', 'search_exact_match_impression_share',
        'search_impression_share', 'search_rank_lost_impression_share', 'search_top_impression_share',
        'top_impression_percentage', 'value_per_all_conversions', 'value_per_conversion',
        'view_through_conversions', 'active_view_cpm', 'active_view_ctr', 'active_view_impressions',
        'active_view_measurability', 'active_view_measurable_cost_micros',
        'active_view_measurable_impressions', 'active_view_viewability', 'ad_group_count',
        'average_cost', 'average_cpc', 'average_cpe', 'average_cpm', 'average_cpv',
        'benchmark_average_max_cpc', 'benchmark_ctr', 'bounce_rate', 'content_budget_lost_impression_share',
        'content_impression_share', 'content_rank_lost_impression_share', 'conversion_rate',
        'cost_per_all_conversions', 'cost_per_current_model_attributed_conversion',
        'current_model_attributed_conversions', 'current_model_attributed_conversion_value',
        'engagement_rate', 'engagements', 'id_campaña'
    ]

def get_campaigns_generator_columns():
    """Columnas de campañas del generador especializado (campaigns_generator.py)"""
    return [
        'estado_campaña', 'campaña', 'presupuesto', 'nombre_presupuesto', 'tipo_presupuesto',
        'estado', 'motivos_estado', 'tipo_campaña', 'impresiones', 'ctr', 'codigo_moneda',
        'costo', 'anuncios_aptos', 'anuncios_rechazados', 'palabras_clave_aptas',
        'palabras_clave_rechazadas', 'grupos_anuncios_aptos', 'anuncios_responsivos_aptos',
        'calidad_anuncio', 'vinculos_aptos_heredados', 'vinculos_aptos_actualizados',
        'imagenes_aptas_heredadas', 'imagenes_aptas_actualizadas', 'resultados',
        'valor_resultados', 'cliente_potencial_llamada', 'conversiones', 'costo_conversion',
        'porcentaje_conversion', 'valor_conversion', 'valor_conversion_costo',
        'valor_conversion_clic', 'valor_por_conversion', 'ajuste_valor',
        'valor_ciclo_cliente_nuevo', 'valor_ciclo_cliente_recuperado', 'conversiones_horario',
        'valor_conversion_horario', 'valor_conversion_por_horario', 'todas_conversiones',
        'costo_todas_conversiones', 'porcentaje_todas_conversiones', 'valor_todas_conversiones',
        'valor_todas_conversiones_costo', 'valor_todas_conversiones_clic',
        'valor_todas_conversiones_por_conversion', 'todos_ajustes_valor',
        'todos_valores_ciclo_cliente_nuevo', 'valor_todos_clientes_recuperados',
        'todas_conversiones_por_horario', 'valor_todas_conversiones_por_horario',
        'valor_por_todas_conversiones_horario', 'pedidos', 'ingresos', 'valor_prom_pedido',
        'unidades_vendidas', 'tamaño_prom_carrito', 'ganancia_bruta', 'margen_ganancia_bruta',
        'costo_bienes_vendidos', 'ingresos_clientes_potenciales', 'unidades_clientes_potenciales',
        'ganancia_bruta_clientes_potenciales', 'costo_bienes_clientes_potenciales',
        'ingresos_ventas_cruzadas', 'unidades_ventas_cruzadas', 'ganancia_ventas_cruzadas',
        'costo_ventas_cruzadas', 'conv_multi_dispositivo', 'valor_conv_multi_dispositivo',
        'conv_multi_dispositivo_horario', 'valor_conv_multi_dispositivo_horario',
        'conv_posimpresion', 'clientes_nuevos', 'clientes_recuperados', 'costo_adquisicion_clientes',
        'conversiones_compras', 'visitas_tienda', 'costo_visita_tienda', 'tasa_visitas_tienda',
        'valor_visitas_tienda', 'valor_visitas_tienda_costo', 'valor_visitas_tienda_interacciones',
        'valor_visitas_tienda_por_visita', 'visitas_tienda_posimpresion', 'conv_comparables',
        'costo_conv_comparables', 'porcentaje_conv_comparables', 'valor_conv_comparables',
        'valor_conv_costo_comparables', 'valor_conv_clic_comparables', 'valor_por_conversion_comparables',
        'conv_comparables_horario', 'valor_conv_comparables_horario', 'valor_por_conversion_comparables_horario',
        'conversiones_modelo_actual', 'costo_conversion_modelo_actual', 'porcentaje_conversion_modelo_actual',
        'valor_conversion_modelo_actual', 'valor_por_conversion_modelo_actual', 'valor_conv_clic_modelo_actual',
        'valor_conv_costo_modelo_actual', 'conversiones_modelo_actual_horario', 'valor_conversion_modelo_actual_horario',
        'valor_por_conversion_modelo_actual_horario', 'visitas_tienda_atribucion_datos', 'visitas_tienda_ultimo_clic',
        'id_campaña', 'subtipo_campaña', 'estrategia_oferta', 'tipo_estrategia_oferta', 'nivel_optimizacion',
        'cpa_objetivo', 'roas_objetivo', 'objetivo_porcentaje_impresiones', 'porcentaje_impresiones_objetivo',
        'limite_oferta_cpc_max', 'etiqueta', 'grupos_campaña', 'margen_optimizacion_cuenta', 'objetivos_conversion',
        'porcentaje_impresiones_busqueda', 'porcentaje_parte_superior_busqueda', 'porcentaje_abs_superior_busqueda',
        'porcentaje_perdido_ranking', 'porcentaje_perdido_clasificacion', 'porcentaje_abs_perdido_clasificacion',
        'porcentaje_perdido_presupuesto', 'porcentaje_perdido_presupuesto_sup', 'porcentaje_abs_perdido_presupuesto_sup',
        'porcentaje_impresion_exacta', 'porcentaje_clics', 'llamadas', 'impresiones_llamadas',
        'porcentaje_llamadas', 'chats', 'impresiones_mensajes', 'tasa_chat', 'cambios_totales',
        'cambios_presupuesto', 'cambios_oferta', 'cambios_palabras_clave', 'cambios_estado',
        'cambios_segmentacion', 'cambios_anuncios', 'cambios_red', 'clics', 'cpc_promedio'
    ]

def analyze_differences():
    """Analiza las diferencias entre los dos generadores"""
    
    ai_columns = set(get_google_ads_generator_campaigns_columns())
    campaigns_columns = set(get_campaigns_generator_columns())
    
    only_in_ai = ai_columns - campaigns_columns
    only_in_campaigns = campaigns_columns - ai_columns
    common = ai_columns & campaigns_columns
    
    print("🔍 ANÁLISIS DE DIFERENCIAS ENTRE GENERADORES")
    print("=" * 60)
    print(f"📊 Columnas en generador IA: {len(ai_columns)}")
    print(f"📊 Columnas en generador campañas: {len(campaigns_columns)}")
    print(f"📊 Columnas en común: {len(common)}")
    print(f"❌ Solo en IA: {len(only_in_ai)}")
    print(f"❌ Solo en campañas: {len(only_in_campaigns)}")
    
    if only_in_ai:
        print(f"\n🔴 COLUMNAS SOLO EN GENERADOR IA ({len(only_in_ai)}):")
        for col in sorted(only_in_ai):
            print(f"   - {col}")
    
    if only_in_campaigns:
        print(f"\n🟡 COLUMNAS SOLO EN GENERADOR CAMPAÑAS ({len(only_in_campaigns)}):")
        for col in sorted(only_in_campaigns):
            print(f"   - {col}")
    
    return only_in_ai, only_in_campaigns

def generate_missing_columns_sql():
    """Genera SQL para agregar las columnas que faltan"""
    
    only_in_ai, only_in_campaigns = analyze_differences()
    
    # Las columnas del generador IA que no están en campañas son las que están causando el error
    missing_columns = only_in_ai
    
    if not missing_columns:
        print("\n✅ No hay columnas faltantes")
        return
    
    print(f"\n🛠️ GENERANDO SQL PARA {len(missing_columns)} COLUMNAS FALTANTES...")
    
    sql_statements = [
        "-- Script para agregar las columnas que faltan del generador IA",
        "-- Estas son las columnas que están causando el error de inserción",
        ""
    ]
    
    for column in sorted(missing_columns):
        # Determinar el tipo de datos
        if 'id_' in column:
            data_type = 'INTEGER'
        elif any(word in column.lower() for word in ['cost', 'costo', 'value', 'valor', 'cpc', 'cpm', 'price', 'precio']):
            data_type = 'DECIMAL(15,2)'
        elif any(word in column.lower() for word in ['rate', 'tasa', 'percentage', 'porcentaje', 'ctr', 'share']):
            data_type = 'DECIMAL(8,4)'
        elif any(word in column.lower() for word in ['impressions', 'impresiones', 'clicks', 'clics', 'conversions', 'conversiones']):
            data_type = 'BIGINT'
        else:
            data_type = 'TEXT'
        
        sql_statements.append(f"ALTER TABLE google_ads_campañas ADD COLUMN IF NOT EXISTS {column} {data_type};")
    
    sql_statements.extend([
        "",
        "-- Verificación",
        "SELECT COUNT(*) as total_columns FROM information_schema.columns",
        "WHERE table_name = 'google_ads_campañas' AND table_schema = 'public';"
    ])
    
    sql_script = '\n'.join(sql_statements)
    
    # Guardar el SQL
    output_file = "fix_missing_ai_columns.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    print(f"✅ Script SQL generado: {output_file}")
    return output_file

def main():
    """Función principal"""
    analyze_differences()
    output_file = generate_missing_columns_sql()
    
    if output_file:
        print(f"\n🚀 PASOS SIGUIENTES:")
        print("1. Ejecuta el script SQL en Supabase")
        print("2. Prueba la inserción nuevamente")

if __name__ == "__main__":
    main()
