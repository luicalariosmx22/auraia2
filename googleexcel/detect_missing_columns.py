"""
Script para detectar automáticamente todas las columnas faltantes en Supabase
y generar el SQL necesario para agregarlas
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

def get_table_columns_from_info_schema(supabase: Client, table_name: str) -> List[str]:
    """Obtiene las columnas de una tabla usando information_schema"""
    try:
        # Usar una consulta SQL directa para obtener columnas
        query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        
        result = supabase.rpc('run_sql', {'query': query}).execute()
        
        if result.data:
            columns = [row['column_name'] for row in result.data]
            return columns
        else:
            print(f"⚠️ No se pudieron obtener columnas para {table_name} via information_schema")
            return []
            
    except Exception as e:
        print(f"❌ Error obteniendo columnas de {table_name}: {str(e)}")
        return []

def get_table_columns_from_sample(supabase: Client, table_name: str) -> List[str]:
    """Obtiene columnas de una tabla mediante consulta de muestra"""
    try:
        result = supabase.table(table_name).select('*').limit(1).execute()
        if result.data and len(result.data) > 0:
            return list(result.data[0].keys())
        else:
            # Si no hay datos, intentar con metadata
            result = supabase.table(table_name).select('*').limit(0).execute()
            return []
    except Exception as e:
        print(f"❌ Error obteniendo columnas de muestra de {table_name}: {str(e)}")
        return []

def get_generator_columns() -> Dict[str, List[str]]:
    """Obtiene las columnas definidas en nuestros generadores"""
    
    # Columnas del generador de anuncios
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
    
    # Columnas del generador de palabras clave
    keywords_columns = [
        'estado_palabra_clave', 'palabra_clave', 'tipo_concordancia', 'campaña', 
        'grupo_anuncios', 'estado', 'motivos_estado', 'url_final', 'url_final_movil',
        'impresiones', 'ctr', 'codigo_moneda', 'costo', 'clics', 'porcentaje_conversion',
        'conversiones', 'cpc_promedio', 'costo_por_conversion', 'id_campaña', 
        'id_grupo_anuncios', 'id_palabra_clave'
    ]
    
    # Columnas del generador de campañas (147 columnas + id_campaña)
    campaigns_columns = [
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
        'id_campaña', 'subtipo_campaña', 'tipo_estrategia_oferta', 'nivel_optimizacion',
        'objetivo_porcentaje_impresiones', 'porcentaje_impresiones_objetivo', 'limite_oferta_cpc_max',
        'etiqueta', 'grupos_campaña', 'margen_optimizacion_cuenta', 'objetivos_conversion',
        'porcentaje_impresiones_busqueda', 'porcentaje_parte_superior_busqueda', 'porcentaje_abs_superior_busqueda',
        'porcentaje_perdido_ranking', 'porcentaje_perdido_clasificacion', 'porcentaje_abs_perdido_clasificacion',
        'porcentaje_perdido_presupuesto', 'porcentaje_perdido_presupuesto_sup', 'porcentaje_abs_perdido_presupuesto_sup',
        'porcentaje_impresion_exacta', 'porcentaje_clics', 'llamadas', 'impresiones_llamadas',
        'porcentaje_llamadas', 'chats', 'impresiones_mensajes', 'tasa_chat', 'cambios_totales',
        'cambios_presupuesto', 'cambios_oferta', 'cambios_palabras_clave', 'cambios_estado',
        'cambios_segmentacion', 'cambios_anuncios', 'cambios_red', 'cpc_promedio',
        'estrategia_oferta', 'cpa_objetivo', 'roas_objetivo'
    ]
    
    return {
        'google_ads_reporte_anuncios': anuncios_columns,
        'google_ads_palabras_clave': keywords_columns,
        'google_ads_campañas': campaigns_columns
    }

def generate_alter_table_sql(missing_columns: Dict[str, List[str]]) -> str:
    """Genera el SQL para agregar las columnas faltantes"""
    
    sql_statements = []
    sql_statements.append("-- Script generado automáticamente para agregar columnas faltantes")
    sql_statements.append("-- Ejecutar en Supabase SQL Editor")
    sql_statements.append("")
    
    for table_name, columns in missing_columns.items():
        if columns:
            sql_statements.append(f"-- Agregar columnas faltantes a {table_name}")
            for column in columns:
                # Determinar el tipo de datos según el nombre de la columna
                if 'id_' in column:
                    data_type = 'INTEGER'
                elif any(word in column.lower() for word in ['costo', 'cost', 'valor', 'value', 'cpc', 'cpm', 'presupuesto', 'budget']):
                    data_type = 'DECIMAL(15,2)'
                elif any(word in column.lower() for word in ['porcentaje', 'percentage', 'ctr', 'tasa', 'rate']):
                    data_type = 'DECIMAL(5,4)'
                elif any(word in column.lower() for word in ['fecha', 'date', 'time']):
                    data_type = 'TIMESTAMP'
                elif any(word in column.lower() for word in ['impresiones', 'impressions', 'clics', 'clicks', 'conversiones', 'conversions']):
                    data_type = 'BIGINT'
                else:
                    data_type = 'TEXT'
                
                sql_statements.append(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column} {data_type};")
            
            sql_statements.append("")
    
    # Agregar índices para las columnas de relación
    sql_statements.append("-- Crear índices para mejorar el rendimiento")
    for table_name in missing_columns.keys():
        if any('id_' in col for col in missing_columns[table_name]):
            for column in missing_columns[table_name]:
                if 'id_' in column:
                    index_name = f"idx_{table_name.replace('google_ads_', '')}_{column}"
                    sql_statements.append(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column});")
    
    sql_statements.append("")
    sql_statements.append("-- Verificar que las columnas se agregaron correctamente")
    sql_statements.append("SELECT table_name, column_name, data_type, is_nullable")
    sql_statements.append("FROM information_schema.columns") 
    sql_statements.append("WHERE table_name IN ('google_ads_campañas', 'google_ads_reporte_anuncios', 'google_ads_palabras_clave')")
    sql_statements.append("ORDER BY table_name, ordinal_position;")
    
    return '\n'.join(sql_statements)

def main():
    """Función principal para detectar columnas faltantes"""
    print("🔍 DETECTANDO COLUMNAS FALTANTES EN SUPABASE")
    print("=" * 60)
    
    try:
        # Conectar a Supabase
        supabase = get_supabase_client()
        print("✅ Conectado a Supabase exitosamente")
        
        # Obtener columnas de los generadores
        generator_columns = get_generator_columns()
        
        # Detectar columnas faltantes por tabla
        missing_columns = {}
        
        for table_name in ['google_ads_campañas', 'google_ads_reporte_anuncios', 'google_ads_palabras_clave']:
            print(f"\n📊 Analizando tabla: {table_name}")
            
            # Intentar obtener columnas de la tabla
            supabase_columns = get_table_columns_from_sample(supabase, table_name)
            
            if not supabase_columns:
                print(f"⚠️ No se pudieron obtener columnas de {table_name} (tabla vacía)")
                # Si no podemos obtener columnas, asumimos que faltan todas las del generador
                missing_columns[table_name] = generator_columns[table_name]
                print(f"📋 Asumiendo que faltan todas las {len(generator_columns[table_name])} columnas del generador")
            else:
                print(f"✅ {len(supabase_columns)} columnas encontradas en Supabase")
                
                # Comparar con las columnas del generador
                expected_columns = set(generator_columns[table_name])
                existing_columns = set(supabase_columns)
                
                missing = expected_columns - existing_columns
                missing_columns[table_name] = list(missing)
                
                print(f"📋 Columnas faltantes: {len(missing)}")
                if missing:
                    print(f"❌ Faltan: {sorted(missing)}")
                else:
                    print("✅ Todas las columnas están presentes")
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE COLUMNAS FALTANTES")
        print("=" * 60)
        
        total_missing = 0
        for table_name, columns in missing_columns.items():
            print(f"\n📋 {table_name}:")
            print(f"   - Faltan: {len(columns)} columnas")
            total_missing += len(columns)
            
            if columns:
                # Mostrar solo las primeras 10 para no saturar la salida
                display_columns = columns[:10]
                print(f"   - Ejemplos: {display_columns}")
                if len(columns) > 10:
                    print(f"   - ... y {len(columns) - 10} más")
        
        print(f"\n📊 TOTAL DE COLUMNAS FALTANTES: {total_missing}")
        
        if total_missing > 0:
            # Generar SQL para agregar columnas faltantes
            print(f"\n🛠️ Generando SQL para agregar columnas faltantes...")
            sql_script = generate_alter_table_sql(missing_columns)
            
            # Guardar el SQL en un archivo
            output_file = "fix_missing_columns.sql"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql_script)
            
            print(f"💾 Script SQL generado: {output_file}")
            print("\n🚀 PASOS SIGUIENTES:")
            print("1. Abre Supabase Dashboard > SQL Editor")
            print(f"2. Copia y pega el contenido de {output_file}")
            print("3. Ejecuta el script SQL")
            print("4. Verifica que las columnas se agregaron correctamente")
            print("5. Vuelve a intentar la inserción de datos")
            
        else:
            print("\n✅ ¡Todas las columnas están presentes! No se requieren cambios.")
            
    except Exception as e:
        print(f"❌ Error durante la detección: {str(e)}")

if __name__ == "__main__":
    main()
