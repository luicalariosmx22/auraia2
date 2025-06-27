import pandas as pd
import os
import re
from typing import List, Optional, Dict

class CampaignsExcelToSQL:
    """Generador específico para la tabla google_ads_campañas"""
    
    def __init__(self):
        # 133 columnas para la tabla google_ads_campañas (según el esquema exacto)
        # Incluye columnas de relación para mantener jerarquía
        self.target_columns = [
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
            'conv_posimpresion', 'clientes_nuevos', 'clientes_recuperados',
            'costo_adquisicion_clientes', 'conversiones_compras', 'visitas_tienda',
            'costo_visita_tienda', 'tasa_visitas_tienda', 'valor_visitas_tienda',
            'valor_visitas_tienda_costo', 'valor_visitas_tienda_interacciones',
            'valor_visitas_tienda_por_visita', 'visitas_tienda_posimpresion', 'conv_comparables',
            'costo_conv_comparables', 'porcentaje_conv_comparables', 'valor_conv_comparables',
            'valor_conv_costo_comparables', 'valor_conv_clic_comparables',
            'valor_por_conversion_comparables', 'conv_comparables_horario',
            'valor_conv_comparables_horario', 'valor_por_conversion_comparables_horario',
            'conversiones_modelo_actual', 'costo_conversion_modelo_actual',
            'porcentaje_conversion_modelo_actual', 'valor_conversion_modelo_actual',
            'valor_por_conversion_modelo_actual', 'valor_conv_clic_modelo_actual',
            'valor_conv_costo_modelo_actual', 'conversiones_modelo_actual_horario',
            'valor_conversion_modelo_actual_horario', 'valor_por_conversion_modelo_actual_horario',
            'visitas_tienda_atribucion_datos', 'visitas_tienda_ultimo_clic', 'id_campaña',
            'subtipo_campaña', 'estrategia_oferta', 'tipo_estrategia_oferta', 'nivel_optimizacion',
            'cpa_objetivo', 'roas_objetivo', 'objetivo_porcentaje_impresiones',
            'porcentaje_impresiones_objetivo', 'limite_oferta_cpc_max', 'etiqueta',
            'grupos_campaña', 'margen_optimizacion_cuenta', 'objetivos_conversion',
            'porcentaje_impresiones_busqueda', 'porcentaje_parte_superior_busqueda',
            'porcentaje_abs_superior_busqueda', 'porcentaje_perdido_ranking',
            'porcentaje_perdido_clasificacion', 'porcentaje_abs_perdido_clasificacion',
            'porcentaje_perdido_presupuesto', 'porcentaje_perdido_presupuesto_sup',
            'porcentaje_abs_perdido_presupuesto_sup', 'porcentaje_impresion_exacta',
            'porcentaje_clics', 'llamadas', 'impresiones_llamadas', 'porcentaje_llamadas',
            'chats', 'impresiones_mensajes', 'tasa_chat', 'cambios_totales',
            'cambios_presupuesto', 'cambios_oferta', 'cambios_palabras_clave', 'cambios_estado',
            'cambios_segmentacion', 'cambios_anuncios', 'cambios_red', 'clics', 'cpc_promedio'
        ]
        
        # Mapeos comunes de Google Ads a nuestra tabla (basado en las 133 columnas)
        self.common_mappings = {
            # Campaña básica
            'Campaign': 'campaña',
            'Campaña': 'campaña',
            'Campaign name': 'campaña',
            'Nombre de campaña': 'campaña',
            'Campaign ID': 'id_campaña',
            'ID de campaña': 'id_campaña',
            
            # Estado y presupuesto
            'Campaign state': 'estado_campaña',
            'Estado de campaña': 'estado_campaña',
            'Status': 'estado',
            'Estado': 'estado',
            'Budget': 'presupuesto',
            'Presupuesto': 'presupuesto',
            'Budget name': 'nombre_presupuesto',
            'Nombre del presupuesto': 'nombre_presupuesto',
            'Budget type': 'tipo_presupuesto',
            'Tipo de presupuesto': 'tipo_presupuesto',
            
            # Tipo de campaña
            'Campaign type': 'tipo_campaña',
            'Tipo de campaña': 'tipo_campaña',
            'Campaign subtype': 'subtipo_campaña',
            'Subtipo de campaña': 'subtipo_campaña',
            
            # Estrategia de oferta
            'Bidding strategy': 'estrategia_oferta',
            'Estrategia de oferta': 'estrategia_oferta',
            'Bidding strategy type': 'tipo_estrategia_oferta',
            'Tipo de estrategia de oferta': 'tipo_estrategia_oferta',
            'Target CPA': 'cpa_objetivo',
            'CPA objetivo': 'cpa_objetivo',
            'Target ROAS': 'roas_objetivo',
            'ROAS objetivo': 'roas_objetivo',
            
            # Métricas básicas
            'Impressions': 'impresiones',
            'Impresiones': 'impresiones',
            'Impr.': 'impresiones',
            'Clicks': 'clics',
            'Clics': 'clics',
            'CTR': 'ctr',
            'Avg. CPC': 'cpc_promedio',
            'CPC prom.': 'cpc_promedio',
            'Prom. CPC': 'cpc_promedio',
            'Cost': 'costo',
            'Costo': 'costo',
            
            # Moneda
            'Currency code': 'codigo_moneda',
            'Código de moneda': 'codigo_moneda',
            
            # Conversiones
            'Conversions': 'conversiones',
            'Conversiones': 'conversiones',
            'Cost/conv.': 'costo_conversion',
            'Costo/conv.': 'costo_conversion',
            'Conv. rate': 'porcentaje_conversion',
            'Porcentaje de conversión': 'porcentaje_conversion',
            'Porcentaje de conv.': 'porcentaje_conversion',
            'Conv. value': 'valor_conversion',
            'Valor de conversión': 'valor_conversion',
            'Value/conv.': 'valor_por_conversion',
            'Valor/conv.': 'valor_por_conversion',
            
            # Todas las conversiones
            'All conv.': 'todas_conversiones',
            'Todas las conv.': 'todas_conversiones',
            'All conv. rate': 'porcentaje_todas_conversiones',
            'Porcentaje de todas las conv.': 'porcentaje_todas_conversiones',
            'All conv. value': 'valor_todas_conversiones',
            'Valor de todas las conv.': 'valor_todas_conversiones',
            
            # Share metrics
            'Search Impr. share': 'porcentaje_impresiones_busqueda',
            'Porcentaje de impresiones de búsqueda': 'porcentaje_impresiones_busqueda',
            'Search top IS': 'porcentaje_parte_superior_busqueda',
            'Search abs. top IS': 'porcentaje_abs_superior_busqueda',
            'Search lost IS (rank)': 'porcentaje_perdido_ranking',
            'Search lost IS (budget)': 'porcentaje_perdido_presupuesto',
            
            # Anuncios y calidad
            'Eligible ads': 'anuncios_aptos',
            'Anuncios aptos': 'anuncios_aptos',
            'Ad strength': 'calidad_anuncio',
            'Nivel del anuncio': 'calidad_anuncio',
            'Calidad del anuncio': 'calidad_anuncio',
            
            # Labels y etiquetas
            'Labels': 'etiqueta',
            'Etiquetas': 'etiqueta',
            'Label': 'etiqueta',
            'Etiqueta': 'etiqueta',
            
            # Grupos de anuncios (para relaciones)
            'Ad group': 'grupo_anuncios',
            'Grupo de anuncios': 'grupo_anuncios',
            'Ad group ID': 'id_grupo_anuncios',
            'ID del grupo de anuncios': 'id_grupo_anuncios'
        }

    def create_mapping(self, excel_columns: List[str]) -> Dict[str, str]:
        """Crea un mapeo de columnas de Excel a columnas de la tabla"""
        mapping = {}
        
        # Aplicar mapeos comunes
        for excel_col in excel_columns:
            excel_col_clean = excel_col.strip()
            if excel_col_clean in self.common_mappings:
                mapping[excel_col_clean] = self.common_mappings[excel_col_clean]
        
        print(f"=== MAPEO CAMPAIGNS ===")
        print(f"Columnas encontradas: {len(excel_columns)}")
        print(f"Mapeos aplicados: {len(mapping)}")
        for excel_col, db_col in mapping.items():
            print(f"  {excel_col} -> {db_col}")
        
        return mapping

    def filter_summary_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra filas de totales/resúmenes que no son campañas reales"""
        print(f"📊 Filas antes del filtrado: {len(df)}")
        
        # Crear una copia para trabajar
        df_filtered = df.copy()
        
        # Lista de patrones que indican filas de totales/resúmenes
        summary_patterns = [
            'todo el período',
            'total:',
            'total ',
            'totales',
            'cuenta',
            'búsqueda',
            'red de display',
            'search network',
            'display network',
            'all campaigns',
            'campaign total',
            'grand total',
            'subtotal',
            'all time',
            'overall'
        ]
        
        # Buscar en todas las columnas de texto para identificar filas de resumen
        mask_to_keep = pd.Series([True] * len(df_filtered))
        
        for col in df_filtered.columns:
            if df_filtered[col].dtype == 'object':  # Solo columnas de texto
                for pattern in summary_patterns:
                    # Crear máscara para filas que NO contienen el patrón
                    pattern_mask = ~df_filtered[col].astype(str).str.lower().str.contains(pattern, na=False)
                    mask_to_keep = mask_to_keep & pattern_mask
        
        # Aplicar filtro
        df_filtered = df_filtered[mask_to_keep]
        
        # Filtro adicional: eliminar filas donde todas las columnas importantes están vacías
        important_cols = ['campaña', 'estado_campaña', 'tipo_campaña']
        available_important_cols = [col for col in important_cols if col in df_filtered.columns]
        
        if available_important_cols:
            # Mantener solo filas que tienen al menos una columna importante con datos
            has_data_mask = df_filtered[available_important_cols].notna().any(axis=1)
            df_filtered = df_filtered[has_data_mask]
        
        print(f"📊 Filas después del filtrado: {len(df_filtered)}")
        print(f"🗑️ Filas de totales eliminadas: {len(df) - len(df_filtered)}")
        
        return df_filtered

    def clean_value(self, value, column_name: str) -> str:
        """Limpia y formatea valores según el tipo de columna"""
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return 'NULL'
        
        value_str = str(value).strip()
        
        # Columnas numéricas que pueden ser NULL
        numeric_columns = [
            'presupuesto', 'impresiones', 'ctr', 'costo', 'clics', 'cpc_promedio',
            'conversiones', 'costo_conversion', 'porcentaje_conversion', 'valor_conversion',
            'todas_conversiones', 'costo_todas_conversiones', 'porcentaje_todas_conversiones',
            'valor_todas_conversiones', 'anuncios_aptos', 'anuncios_rechazados',
            'palabras_clave_aptas', 'palabras_clave_rechazadas', 'grupos_anuncios_aptos',
            'porcentaje_impresiones_busqueda', 'porcentaje_parte_superior_busqueda',
            'porcentaje_abs_superior_busqueda', 'porcentaje_perdido_ranking',
            'porcentaje_perdido_presupuesto', 'llamadas', 'impresiones_llamadas',
            'porcentaje_llamadas', 'chats', 'tasa_chat', 'cambios_totales'
        ]
        
        if column_name in numeric_columns:
            try:
                # Limpiar caracteres especiales de números
                clean_num = value_str.replace(',', '').replace('%', '').replace('$', '').replace('€', '')
                clean_num = clean_num.replace('--', '').replace('-', '').strip()
                
                if clean_num == '' or clean_num == '0.00' or clean_num == '0':
                    return '0'
                
                float_val = float(clean_num)
                return str(float_val)
            except (ValueError, TypeError):
                return '0'
        
        # Columnas de texto - escapar comillas simples
        value_str = value_str.replace("'", "''")
        return f"'{value_str}'"

    def generate_insert_sql(self, df_mapped: pd.DataFrame) -> List[str]:
        """Genera sentencias INSERT SQL"""
        sql_statements = []
        
        # Crear la sentencia INSERT base
        table_name = "public.google_ads_campañas"
        columns_str = ', '.join(self.target_columns)
        
        for _, row in df_mapped.iterrows():
            values = []
            for col in self.target_columns:
                value = row.get(col, None)
                cleaned_value = self.clean_value(value, col)
                values.append(cleaned_value)
            
            values_str = ', '.join(values)
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"
            sql_statements.append(sql)
        
        return sql_statements

    def process_excel_to_sql(self, excel_file: str, output_file: str, sheet_name: Optional[str] = None) -> bool:
        """Procesa un archivo Excel y genera SQL para campañas"""
        try:
            print(f"=== CAMPAIGNS PROCESSOR ===")
            print(f"Archivo Excel: {excel_file}")
            print(f"Archivo salida: {output_file}")
            print(f"Hoja: {sheet_name}")
            
            # Leer Excel
            if sheet_name:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_file)
            
            print(f"Datos leídos: {len(df)} filas, {len(df.columns)} columnas")
            
            # Limpiar columnas Unnamed y vacías
            df = self._clean_unnamed_columns(df)
            
            print(f"Después de limpieza: {len(df)} filas, {len(df.columns)} columnas")
            print(f"Columnas válidas encontradas: {list(df.columns)}")
            
            # Filtrar filas de totales/resúmenes
            df = self.filter_summary_rows(df)
            
            if len(df) == 0:
                print("❌ ERROR: No se encontraron campañas válidas después del filtrado")
                return False
            
            # Limpiar columnas innecesarias
            df = self._clean_unnamed_columns(df)
            
            # Crear mapeo
            mapping = self.create_mapping(list(df.columns))
            
            if not mapping:
                print("ERROR: No se pudo crear mapeo de columnas")
                return False
            
            # Crear DataFrame con columnas mapeadas
            df_mapped = pd.DataFrame()
            
            # Mapear columnas conocidas
            for excel_col, db_col in mapping.items():
                if excel_col in df.columns:
                    df_mapped[db_col] = df[excel_col]
            
            # Agregar columnas faltantes en un solo paso para evitar fragmentación
            missing_columns = {}
            for col in self.target_columns:
                if col not in df_mapped.columns:
                    missing_columns[col] = None
                    print(f"Columna faltante rellenada con NULL: {col}")
            
            # Usar pd.concat para agregar todas las columnas faltantes de una vez
            if missing_columns:
                missing_df = pd.DataFrame(missing_columns, index=df_mapped.index)
                df_mapped = pd.concat([df_mapped, missing_df], axis=1)
            
            # Reordenar columnas según el orden de la tabla y desfragmentar
            df_mapped = df_mapped[self.target_columns].copy()
            
            print(f"DataFrame final: {len(df_mapped)} filas, {len(df_mapped.columns)} columnas")
            
            # Generar SQL
            sql_statements = self.generate_insert_sql(df_mapped)
            
            # Escribir archivo
            output_dir = os.path.dirname(output_file)
            if output_dir:  # Solo crear directorio si hay uno
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Escribir encabezado
                f.write("-- SQL generado para google_ads_campañas\n")
                f.write(f"-- Archivo origen: {os.path.basename(excel_file)}\n")
                f.write(f"-- Registros: {len(sql_statements)}\n")
                f.write(f"-- Generado: {pd.Timestamp.now()}\n\n")
                
                # Escribir sentencias SQL
                for sql in sql_statements:
                    f.write(sql + '\n')
            
            print(f"✅ SQL generado exitosamente: {len(sql_statements)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Error procesando campaigns: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

    def _clean_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina columnas 'Unnamed' y otras columnas vacías o inútiles"""
        initial_columns = len(df.columns)
        
        # Lista de patrones de columnas a eliminar
        patterns_to_remove = [
            r'^Unnamed:',           # Unnamed: 0, Unnamed: 1, etc.
            r'^Unnamed\s*\d*$',     # Unnamed, Unnamed1, Unnamed2, etc.
            r'^\s*$',               # Columnas con nombres vacíos
            r'^Column\d*$',         # Column1, Column2, etc.
            r'^Total\s*$',          # Columnas de totales
            r'^Subtotal\s*$',       # Columnas de subtotales
            r'^Grand Total\s*$',    # Grand Total
            r'^Total general\s*$',  # Total general (español)
        ]
        
        # Columnas a mantener (antes del filtrado)
        columns_to_keep = []
        removed_columns = []
        
        for col in df.columns:
            col_str = str(col)
            should_remove = False
            
            # Verificar patrones de eliminación
            for pattern in patterns_to_remove:
                if re.match(pattern, col_str, re.IGNORECASE):
                    should_remove = True
                    break
            
            # Verificar si la columna está completamente vacía
            if not should_remove and df[col].isna().all():
                should_remove = True
            
            # Verificar si la columna tiene solo valores vacíos o espacios
            if not should_remove:
                non_null_values = df[col].dropna().astype(str).str.strip()
                if len(non_null_values) == 0 or non_null_values.eq('').all():
                    should_remove = True
            
            if should_remove:
                removed_columns.append(col_str)
            else:
                columns_to_keep.append(col)
        
        # Filtrar DataFrame
        df_cleaned = df[columns_to_keep].copy()
        
        print(f"🗑️ Columnas eliminadas ({len(removed_columns)}): {removed_columns}")
        print(f"✅ Columnas conservadas ({len(columns_to_keep)}): {[str(col) for col in columns_to_keep]}")
        
        return df_cleaned
def test_campaigns_generator():
    """Función de prueba para el generador de campaigns"""
    # Crear datos de ejemplo
    test_data = {
        'Campaign': ['SaldeJade - Search Campaign', 'SaldeJade - Display Campaign'],
        'Campaign state': ['Enabled', 'Paused'],
        'Campaign type': ['Search', 'Display'],
        'Budget': [1500.00, 800.00],
        'Impressions': [15000, 8500],
        'Clicks': [450, 120],
        'CTR': ['3.00%', '1.41%'],
        'Cost': [675.50, 180.30],
        'Conversions': [15, 3],
        'Cost/conv.': [45.03, 60.10]
    }
    
    df = pd.DataFrame(test_data)
    
    # Crear archivo Excel temporal
    test_excel = 'test_campaigns.xlsx'
    df.to_excel(test_excel, index=False)
    
    # Procesar
    generator = CampaignsExcelToSQL()
    success = generator.process_excel_to_sql(test_excel, 'test_campaigns_output.sql')
    
    # Limpiar
    if os.path.exists(test_excel):
        os.remove(test_excel)
    
    return success


if __name__ == "__main__":
    print("📈 Testing Campaigns Generator...")
    success = test_campaigns_generator()
    print(f"Test result: {'✅ Success' if success else '❌ Failed'}")
