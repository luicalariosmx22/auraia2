"""
Script para agregar específicamente las columnas faltantes de la tabla google_ads_campañas
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

def get_expected_campaigns_columns():
    """Obtiene todas las columnas que el generador de campañas necesita"""
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

def generate_campaigns_sql():
    """Genera el SQL para agregar todas las columnas de campañas"""
    
    expected_columns = get_expected_campaigns_columns()
    
    sql_statements = [
        "-- Script para agregar TODAS las columnas faltantes de google_ads_campañas",
        "-- Ejecutar en Supabase SQL Editor",
        ""
    ]
    
    for column in expected_columns:
        # Determinar el tipo de datos según el nombre de la columna
        if 'id_' in column:
            data_type = 'INTEGER'
        elif any(word in column.lower() for word in ['costo', 'cost', 'valor', 'value', 'cpc', 'cpm', 'presupuesto', 'budget', 'precio', 'price']):
            data_type = 'DECIMAL(15,2)'
        elif any(word in column.lower() for word in ['porcentaje', 'percentage', 'ctr', 'tasa', 'rate', 'margen', 'margin']):
            data_type = 'DECIMAL(8,4)'
        elif any(word in column.lower() for word in ['impresiones', 'impressions', 'clics', 'clicks', 'conversiones', 'conversions', 'unidades']):
            data_type = 'BIGINT'
        else:
            data_type = 'TEXT'
        
        sql_statements.append(f"ALTER TABLE google_ads_campañas ADD COLUMN IF NOT EXISTS {column} {data_type};")
    
    sql_statements.extend([
        "",
        "-- Crear índices para columnas de relación",
        "CREATE INDEX IF NOT EXISTS idx_campañas_id_campaña ON google_ads_campañas(id_campaña);",
        "CREATE INDEX IF NOT EXISTS idx_campañas_campaña ON google_ads_campañas(campaña);",
        "CREATE INDEX IF NOT EXISTS idx_campañas_estado ON google_ads_campañas(estado_campaña);",
        "",
        "-- Verificación final",
        "SELECT COUNT(*) as total_columns FROM information_schema.columns",
        "WHERE table_name = 'google_ads_campañas' AND table_schema = 'public';"
    ])
    
    return '\n'.join(sql_statements)

def main():
    """Genera el script SQL específico para campañas"""
    print("🔧 GENERANDO SCRIPT SQL PARA CAMPAÑAS")
    print("=" * 50)
    
    sql_script = generate_campaigns_sql()
    
    # Guardar el SQL en un archivo
    output_file = "fix_campaigns_columns.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    print(f"✅ Script SQL generado: {output_file}")
    print(f"📊 Columnas a agregar: {len(get_expected_campaigns_columns())}")
    
    print("\n🚀 PASOS SIGUIENTES:")
    print("1. Abre Supabase Dashboard > SQL Editor")
    print(f"2. Copia y pega el contenido de {output_file}")
    print("3. Ejecuta el script SQL")
    print("4. Prueba la inserción nuevamente")

if __name__ == "__main__":
    main()
