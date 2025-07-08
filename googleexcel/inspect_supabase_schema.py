"""
Script para inspeccionar el esquema actual de las tablas de Supabase
y comparar con las columnas que generan nuestros scripts
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Dict, List
import json

# Cargar variables de entorno
load_dotenv()

def get_supabase_client():
    """Inicializa cliente de Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("❌ Error: SUPABASE_URL y SUPABASE_ANON_KEY deben estar configuradas en .env")
    
    return create_client(supabase_url, supabase_key)

def inspect_table_schema(supabase: Client, table_name: str) -> Dict:
    """Inspecciona el esquema de una tabla específica"""
    try:
        # Obtener un registro de muestra para ver las columnas
        result = supabase.table(table_name).select('*').limit(1).execute()
        
        # Si no hay datos, intentar una inserción de prueba para ver qué columnas acepta
        if not result.data:
            print(f"⚠️ Tabla {table_name} está vacía, no se pueden determinar las columnas exactas")
            return {
                'table': table_name,
                'columns': [],
                'sample_data': None,
                'status': 'empty'
            }
        
        sample_record = result.data[0]
        columns = list(sample_record.keys())
        
        return {
            'table': table_name,
            'columns': columns,
            'sample_data': sample_record,
            'status': 'has_data'
        }
        
    except Exception as e:
        return {
            'table': table_name,
            'error': str(e),
            'status': 'error'
        }

def get_generator_columns() -> Dict:
    """Obtiene las columnas definidas en nuestros generadores"""
    
    # Columnas del generador de Google Ads (IA)
    anuncios_columns = [
        'estado_anuncio', 'url_final', 'titulo_1', 'pos_titulo_1', 'titulo_2', 'pos_titulo_2',
        'titulo_3', 'pos_titulo_3', 'titulo_4', 'pos_titulo_4', 'titulo_5', 'pos_titulo_5',
        'titulo_6', 'pos_titulo_6', 'titulo_7', 'pos_titulo_7', 'titulo_8', 'pos_titulo_8',
        'titulo_9', 'pos_titulo_9', 'titulo_10', 'pos_titulo_10', 'titulo_11', 'pos_titulo_11',
        'titulo_12', 'pos_titulo_12', 'titulo_13', 'pos_titulo_13', 'titulo_14', 'pos_titulo_14',
        'titulo_15', 'pos_titulo_15', 'descripcion_1', 'pos_desc_1', 'descripcion_2', 'pos_desc_2',
        'descripcion_3', 'pos_desc_3', 'descripcion_4', 'pos_desc_4', 'ruta_1', 'ruta_2',
        'url_final_movil', 'plantilla_seguimiento', 'sufijo_url_final', 'param_personalizado',
        'campaña', 'grupo_anuncios', 'estado', 'motivos_estado', 'calidad_anuncio',
        'mejoras_efectividad', 'tipo_anuncio', 'clics', 'impresiones', 'ctr', 'codigo_moneda',
        'cpc_promedio', 'costo', 'porcentaje_conversion', 'conversiones', 'costo_por_conversion',
        'id_campaña', 'id_grupo_anuncios', 'id_anuncio'
    ]
    
    keywords_columns = [
        'estado_palabra_clave', 'palabra_clave', 'tipo_concordancia', 'campaña', 
        'grupo_anuncios', 'estado', 'motivos_estado', 'url_final', 'url_final_movil',
        'impresiones', 'ctr', 'codigo_moneda', 'costo', 'clics', 'porcentaje_conversion',
        'conversiones', 'cpc_promedio', 'costo_por_conversion', 'id_campaña', 
        'id_grupo_anuncios', 'id_palabra_clave'
    ]
    
    campaigns_columns = [
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
    
    return {
        'google_ads_reporte_anuncios': anuncios_columns,
        'google_ads_palabras_clave': keywords_columns,
        'google_ads_campañas': campaigns_columns
    }

def compare_schemas(supabase_schemas: Dict, generator_columns: Dict) -> Dict:
    """Compara los esquemas de Supabase con las columnas de los generadores"""
    
    comparison = {}
    
    for table_name in ['google_ads_campañas', 'google_ads_reporte_anuncios', 'google_ads_palabras_clave']:
        supabase_schema = supabase_schemas.get(table_name, {})
        generator_cols = set(generator_columns.get(table_name, []))
        
        if supabase_schema.get('status') == 'has_data':
            supabase_cols = set(supabase_schema['columns'])
            
            missing_in_supabase = generator_cols - supabase_cols
            missing_in_generator = supabase_cols - generator_cols
            common_columns = generator_cols & supabase_cols
            
            comparison[table_name] = {
                'supabase_columns_count': len(supabase_cols),
                'generator_columns_count': len(generator_cols),
                'common_columns_count': len(common_columns),
                'missing_in_supabase': list(missing_in_supabase),
                'missing_in_generator': list(missing_in_generator),
                'status': 'compared'
            }
        else:
            comparison[table_name] = {
                'status': supabase_schema.get('status', 'unknown'),
                'error': supabase_schema.get('error'),
                'generator_columns_count': len(generator_cols)
            }
    
    return comparison

def main():
    """Función principal para inspeccionar esquemas"""
    print("🔍 INSPECCIONANDO ESQUEMAS DE SUPABASE")
    print("=" * 50)
    
    try:
        # Conectar a Supabase
        supabase = get_supabase_client()
        print("✅ Conectado a Supabase exitosamente")
        
        # Inspeccionar tablas
        tables = ['google_ads_campañas', 'google_ads_reporte_anuncios', 'google_ads_palabras_clave']
        supabase_schemas = {}
        
        for table in tables:
            print(f"\n📊 Inspeccionando tabla: {table}")
            schema = inspect_table_schema(supabase, table)
            supabase_schemas[table] = schema
            
            if schema['status'] == 'has_data':
                print(f"✅ {len(schema['columns'])} columnas encontradas")
            elif schema['status'] == 'empty':
                print("⚠️ Tabla vacía")
            else:
                print(f"❌ Error: {schema.get('error')}")
        
        # Obtener columnas de generadores
        print("\n📝 Obteniendo columnas de generadores...")
        generator_columns = get_generator_columns()
        
        # Comparar esquemas
        print("\n🔄 Comparando esquemas...")
        comparison = compare_schemas(supabase_schemas, generator_columns)
        
        # Mostrar resultados
        print("\n" + "=" * 50)
        print("📊 RESULTADOS DE LA COMPARACIÓN")
        print("=" * 50)
        
        for table_name, comp in comparison.items():
            print(f"\n📋 TABLA: {table_name}")
            print("-" * 40)
            
            if comp['status'] == 'compared':
                print(f"🔹 Columnas en Supabase: {comp['supabase_columns_count']}")
                print(f"🔹 Columnas en generador: {comp['generator_columns_count']}")
                print(f"🔹 Columnas en común: {comp['common_columns_count']}")
                
                if comp['missing_in_supabase']:
                    print(f"\n❌ FALTAN EN SUPABASE ({len(comp['missing_in_supabase'])} columnas):")
                    for col in sorted(comp['missing_in_supabase']):
                        print(f"   - {col}")
                
                if comp['missing_in_generator']:
                    print(f"\n⚠️ SOLO EN SUPABASE ({len(comp['missing_in_generator'])} columnas):")
                    for col in sorted(comp['missing_in_generator']):
                        print(f"   - {col}")
                
                if not comp['missing_in_supabase'] and not comp['missing_in_generator']:
                    print("✅ Esquemas coinciden perfectamente")
                    
            else:
                print(f"❌ Estado: {comp['status']}")
                if comp.get('error'):
                    print(f"❌ Error: {comp['error']}")
                print(f"🔹 Columnas en generador: {comp['generator_columns_count']}")
        
        # Guardar resultados en archivo JSON
        results = {
            'supabase_schemas': supabase_schemas,
            'generator_columns': generator_columns,
            'comparison': comparison,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open('schema_comparison.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: schema_comparison.json")
        
    except Exception as e:
        print(f"❌ Error durante la inspección: {str(e)}")

if __name__ == "__main__":
    import pandas as pd
    main()
