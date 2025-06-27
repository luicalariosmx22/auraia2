import pandas as pd
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Optional
import re

# Cargar variables de entorno
load_dotenv()

class GoogleAdsExcelAnalyzer:
    def __init__(self):
        """Inicializa el analizador con la configuración de OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ Error: OPENAI_API_KEY debe estar configurada en el archivo .env")
        self.client = OpenAI(api_key=api_key)
        
        # Definir las columnas de la tabla de anuncios (65 columnas con relaciones)
        self.anuncios_columns = [
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
        
        # Definir las columnas de la tabla de palabras clave (21 columnas con relaciones)
        self.keywords_columns = [
            'estado_palabra_clave', 'palabra_clave', 'tipo_concordancia', 'campaña', 
            'grupo_anuncios', 'estado', 'motivos_estado', 'url_final', 'url_final_movil',
            'impresiones', 'ctr', 'codigo_moneda', 'costo', 'clics', 'porcentaje_conversion',
            'conversiones', 'cpc_promedio', 'costo_por_conversion', 'id_campaña', 
            'id_grupo_anuncios', 'id_palabra_clave'
        ]
        
        # Definir las columnas de la tabla de campañas (136 columnas con relaciones)
        self.campaigns_columns = [
            'estado_campaña', 'campaña', 'presupuesto', 'nombre_presupuesto', 'tipo_presupuesto',
            'estado', 'motivos_estado', 'tipo_campaña', 'impresiones', 'ctr', 'codigo_moneda',
            'costo', 'anuncios_aptos', 'anuncios_rechazados', 'palabras_clave_aptas',
            'palabras_clave_rechazadas', 'grupos_anuncios_aptos', 'anuncios_responsivos_aptos',
            'calidad_anuncio', 'vinculos_aptos_heredados', 'vinculos_aptos_actualizados',
            'imagenes_aptas_heredadas', 'imagenes_aptas_actualizadas', 'resultados',
            'valor_resultados', 'cliente_potencial_llamada', 'conversiones', 'costo_conversion',
            'costo_por_conversion', 'porcentaje_conversion', 'valor_conversion', 'conversiones_vista', 'costo_conversion_vista',
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
        
        # Columnas por defecto (anuncios)
        self.target_columns = self.anuncios_columns
        self.table_type = 'anuncios'
    
    def set_table_type(self, table_type: str):
        """Configura el tipo de tabla a procesar"""
        self.table_type = table_type
        
        # Normalizar nombres en inglés y español
        if table_type in ['palabras_clave', 'keywords']:
            self.target_columns = self.keywords_columns
            self.table_type = 'palabras_clave'
        elif table_type in ['campañas', 'campaigns']:
            self.target_columns = self.campaigns_columns
            self.table_type = 'campañas'
        else:
            self.target_columns = self.anuncios_columns
            self.table_type = 'anuncios'
        
        print(f"🎯 Configurado para tabla: {self.table_type} ({len(self.target_columns)} columnas)")

    def read_excel_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Lee el archivo Excel y retorna un DataFrame limpio sin columnas Unnamed"""
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            print(f"✅ Archivo Excel leído exitosamente: {file_path}")
            print(f"📊 Dimensiones originales: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Limpiar columnas Unnamed
            df = self._clean_unnamed_columns(df)
            
            print(f"� Dimensiones después de limpieza: {df.shape[0]} filas, {df.shape[1]} columnas")
            print(f"�🔍 Columnas válidas encontradas: {list(df.columns)}")
            
            return df
        except Exception as e:
            print(f"❌ Error al leer el archivo Excel: {str(e)}")
            raise

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

    def analyze_excel_structure(self, df: pd.DataFrame) -> Dict:
        """Usa OpenAI para analizar la estructura del Excel y mapear columnas"""
        try:
            # Para campañas con muchas columnas, reducir el contexto
            if self.table_type == 'campañas' and len(df.columns) > 50:
                sample_size = 2
                essential_cols = [col for col in df.columns if any(keyword in col.lower() 
                                for keyword in ['campaign', 'campaña', 'cost', 'costo', 'click', 
                                                  'clic', 'impression', 'impresión', 'conversion', 
                                                  'conversión', 'budget', 'presupuesto', 'status', 
                                                  'estado', 'type', 'tipo'])][:20]
                sample_data = df[essential_cols].head(sample_size).to_dict('records') if essential_cols else []
            else:
                sample_size = 3
                sample_data = df.head(sample_size).to_dict('records')
            
            # Escapar caracteres especiales en los datos de muestra
            safe_sample_data = []
            for record in sample_data:
                safe_record = {}
                for k, v in record.items():
                    if isinstance(v, str):
                        # Escapar caracteres especiales
                        v = v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    safe_record[str(k)] = str(v)
                safe_sample_data.append(safe_record)
            
            # Preparar información del Excel optimizada
            excel_info = {
                "columns": [str(col) for col in df.columns],
                "sample_data": safe_sample_data,
                "total_columns": len(df.columns),
                "total_rows": len(df)
            }
            
            # Prompt optimizado para OpenAI
            if self.table_type == 'anuncios':
                table_description = "anuncios (ads)"
                table_name = "google_ads_reporte_anuncios"
                specific_instruction = "Identifica títulos numerados (titulo_1, titulo_2, etc.)"
            elif self.table_type == 'palabras_clave':
                table_description = "palabras clave (keywords)"
                table_name = "google_ads_palabras_clave"
                specific_instruction = "Enfócate en keywords, match types y métricas"
            else:  # campañas
                table_description = "campañas (campaigns)"
                table_name = "google_ads_campañas"
                specific_instruction = "Enfócate en campaign names, budgets y métricas de campaña"
            
            # Generar prompt seguro
            prompt = f"""Mapea columnas Excel de Google Ads a tabla Supabase {table_name}.

EXCEL COLUMNS ({len(excel_info['columns'])}):
{json.dumps(excel_info['columns'][:50], ensure_ascii=False)}

TARGET COLUMNS ({len(self.target_columns)}):
{json.dumps(self.target_columns, ensure_ascii=False)}

SAMPLE DATA:
{json.dumps(excel_info['sample_data'][:2], ensure_ascii=False)}

{specific_instruction}

IMPORTANTE: La respuesta debe ser un JSON válido con este formato:
{{
    "column_mapping": {{
        "excel_column1": "target_column1",
        "excel_column2": "target_column2"
    }},
    "confidence_score": 0.95
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de datos de Google Ads y bases de datos. Responde solo con JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parsear respuesta asegurándonos de que es JSON válido
            try:
                analysis = json.loads(response.choices[0].message.content)
                print("🤖 Análisis de OpenAI completado:")
                print(f"🎯 Confidence Score: {analysis.get('confidence_score', 'N/A')}")
                print(f"📋 Mapeos encontrados: {len(analysis.get('column_mapping', {}))}")
                return analysis
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {str(e)}")
                print("Respuesta recibida:", response.choices[0].message.content)
                raise
            
        except Exception as e:
            print(f"❌ Error en el análisis con OpenAI: {str(e)}")
            raise

    def apply_column_mapping(self, df: pd.DataFrame, mapping: Dict) -> pd.DataFrame:
        """Aplica el mapeo de columnas al DataFrame"""
        
        # Crear nuevo DataFrame con las columnas mapeadas
        mapped_df = pd.DataFrame()
        
        for excel_col, target_col in mapping['column_mapping'].items():
            if excel_col in df.columns and target_col != "no_mapping":
                mapped_df[target_col] = df[excel_col]
        
        # Agregar columnas faltantes como NULL
        for col in self.target_columns:
            if col not in mapped_df.columns:
                mapped_df[col] = None
        
        # Reordenar columnas según el orden de la tabla destino
        mapped_df = mapped_df[self.target_columns]
        
        print(f"🔄 Mapeo aplicado. Nuevo DataFrame: {mapped_df.shape}")
        return mapped_df

    def clean_and_validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y valida los datos antes de generar SQL"""
        
        cleaned_df = df.copy()
        
        # Si es tabla de palabras clave o campañas, filtrar filas de totales
        if self.table_type in ['palabras_clave', 'campañas']:
            cleaned_df = self.filter_summary_rows(cleaned_df)
        
        # Limpiar valores
        for col in cleaned_df.columns:
            # Convertir a string y limpiar
            cleaned_df[col] = cleaned_df[col].astype(str)
            cleaned_df[col] = cleaned_df[col].replace('nan', '')
            cleaned_df[col] = cleaned_df[col].replace('None', '')
            cleaned_df[col] = cleaned_df[col].replace('<NA>', '')
            
            # Escapar comillas simples para SQL
            cleaned_df[col] = cleaned_df[col].str.replace("'", "''")
            
            # Convertir valores vacíos a NULL
            cleaned_df[col] = cleaned_df[col].replace('', None)
        
        print(f"🧹 Datos limpiados y validados")
        return cleaned_df

    def filter_summary_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra filas de totales/resúmenes que no son palabras clave reales"""
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
            'all ad groups',
            'all keywords',
            'campaign total',
            'ad group total',
            'keyword total',
            'grand total',
            'subtotal'
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
        if self.table_type == 'palabras_clave':
            important_cols = ['palabra_clave', 'campaña', 'grupo_anuncios']
        elif self.table_type == 'campañas':
            important_cols = ['campaña', 'estado_campaña', 'tipo_campaña']
        else:  # anuncios
            important_cols = ['campaña', 'grupo_anuncios', 'tipo_anuncio']
        
        available_important_cols = [col for col in important_cols if col in df_filtered.columns]
        
        if available_important_cols:
            # Mantener solo filas que tienen al menos una columna importante con datos
            has_data_mask = df_filtered[available_important_cols].notna().any(axis=1)
            df_filtered = df_filtered[has_data_mask]
        
        print(f"📊 Filas después del filtrado: {len(df_filtered)}")
        print(f"🗑️ Filas de totales eliminadas: {len(df) - len(df_filtered)}")
        
        return df_filtered

    def generate_sql_inserts(self, df: pd.DataFrame) -> List[str]:
        """Genera las sentencias SQL INSERT"""
        
        # Determinar nombre de tabla según el tipo
        if self.table_type == 'anuncios':
            table_name = "public.google_ads_reporte_anuncios"
        elif self.table_type == 'palabras_clave':
            table_name = "public.google_ads_palabras_clave"
        else:  # campañas
            table_name = "public.google_ads_campañas"
        
        sql_statements = []
        
        # Generar INSERT para cada fila
        for index, row in df.iterrows():
            values = []
            for col in self.target_columns:
                value = row[col]
                if pd.isna(value) or value is None or value == '':
                    values.append('NULL')
                else:
                    # Escapar y envolver en comillas simples
                    values.append(f"'{str(value)}'")
            
            values_str = ', '.join(values)
            
            sql = f"""INSERT INTO {table_name} (
    {', '.join(self.target_columns)}
) VALUES (
    {values_str}
);"""
            
            sql_statements.append(sql)
        
        print(f"📝 Generadas {len(sql_statements)} sentencias SQL INSERT")
        return sql_statements

    def save_sql_to_file(self, sql_statements: List[str], output_file: str):
        """Guarda las sentencias SQL en un archivo"""
        
        if self.table_type == 'anuncios':
            table_name = "public.google_ads_reporte_anuncios"
            table_description = "anuncios"
        elif self.table_type == 'palabras_clave':
            table_name = "public.google_ads_palabras_clave"
            table_description = "palabras clave"
        else:  # campañas
            table_name = "public.google_ads_campañas"
            table_description = "campañas"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Sentencias SQL generadas automáticamente para Google Ads ({table_description})\n")
            f.write(f"-- Tabla destino: {table_name}\n")
            f.write(f"-- Fecha de generación: {pd.Timestamp.now()}\n\n")
            
            for i, sql in enumerate(sql_statements, 1):
                f.write(f"-- Registro {i}\n")
                f.write(sql)
                f.write("\n\n")
        
        print(f"💾 Archivo SQL guardado: {output_file}")

    def process_excel_to_sql(self, excel_file: str, output_file: str = "google_ads_inserts.sql", sheet_name: Optional[str] = None, table_type: str = 'anuncios'):
        """Proceso completo: Excel → Análisis IA → SQL"""
        
        print("🚀 Iniciando proceso de conversión Excel → SQL")
        print("=" * 50)
        
        # Configurar tipo de tabla
        self.set_table_type(table_type)
        
        try:
            # 1. Leer Excel
            df = self.read_excel_file(excel_file, sheet_name)
            
            # 2. Analizar con IA (con fallback si falla)
            print("\n🤖 Analizando estructura con OpenAI...")
            try:
                analysis = self.analyze_excel_structure(df)
            except Exception as ai_error:
                print(f"⚠️ Error con OpenAI: {str(ai_error)}")
                if "context_length_exceeded" in str(ai_error) or "8192 tokens" in str(ai_error):
                    print("📋 Usando generador simple como alternativa...")
                    return self.fallback_to_simple_generator(excel_file, output_file, sheet_name, table_type)
                else:
                    raise ai_error
            
            # 3. Mostrar resultados del análisis
            print(f"\n📊 RESULTADOS DEL ANÁLISIS:")
            print(f"✅ Columnas mapeadas: {len(analysis['column_mapping'])}")
            print(f"⚠️ Columnas Excel sin mapeo: {len(analysis.get('unmapped_excel_columns', []))}")
            print(f"⚠️ Columnas destino sin datos: {len(analysis.get('unmapped_target_columns', []))}")
            
            # 4. Detectar relaciones jerárquicas automáticamente
            print("\n🔗 Detectando relaciones jerárquicas...")
            relationships = self.detect_hierarchical_relationships(df)
            
            # 5. Aplicar mapeo
            print("\n🔄 Aplicando mapeo de columnas...")
            mapped_df = self.apply_column_mapping(df, analysis)
            
            # 6. Asignar IDs relacionales
            print("\n🆔 Asignando IDs relacionales...")
            mapped_df = self.assign_relational_ids(mapped_df, relationships)
            
            # 7. Limpiar datos
            print("\n🧹 Limpiando y validando datos...")
            clean_df = self.clean_and_validate_data(mapped_df)
            
            # 8. Generar SQL
            print("\n📝 Generando sentencias SQL...")
            sql_statements = self.generate_sql_inserts(clean_df)
            
            # 9. Guardar archivo
            print("\n💾 Guardando archivo SQL...")
            self.save_sql_to_file(sql_statements, output_file)
            
            print("\n✅ PROCESO COMPLETADO EXITOSAMENTE!")
            print("=" * 50)
            print(f"📁 Archivo SQL generado: {output_file}")
            print(f"📊 Total de registros: {len(sql_statements)}")
            
            return {
                'success': True,
                'output_file': output_file,
                'total_records': len(sql_statements),
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"\n❌ ERROR EN EL PROCESO: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def fallback_to_simple_generator(self, excel_file: str, output_file: str, sheet_name: Optional[str] = None, table_type: str = 'anuncios'):
        """Fallback al generador simple cuando OpenAI falla por límites de contexto"""
        try:
            print("🔄 Activando fallback al generador simple...")
            
            if table_type == 'campañas':
                from campaigns_generator import CampaignsExcelToSQL
                generator = CampaignsExcelToSQL()
                success = generator.process_excel_to_sql(excel_file, output_file, sheet_name)
            elif table_type == 'palabras_clave':
                from keywords_generator import KeywordsExcelToSQL
                generator = KeywordsExcelToSQL()
                success = generator.process_excel_to_sql(excel_file, output_file, sheet_name)
            else:  # anuncios
                from simple_excel_to_sql import SimpleExcelToSQL
                generator = SimpleExcelToSQL()
                success = generator.process_excel_simple(excel_file, output_file, sheet_name, table_type)
            
            if success:
                # Contar registros generados
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        record_count = content.count('INSERT INTO')
                except:
                    record_count = 0
                
                return {
                    'success': True,
                    'total_records': record_count,
                    'analysis': {
                        'method': 'simple_fallback',
                        'reason': 'OpenAI context limit exceeded',
                        'table_type': table_type
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Fallback al generador simple también falló'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en fallback simple: {str(e)}'
            }

    def detect_hierarchical_relationships(self, df: pd.DataFrame) -> Dict:
        """Detecta automáticamente las relaciones jerárquicas en los datos de Google Ads"""
        
        relationships = {
            'campaigns': {},      # {'nombre_campaña': id_campaña}
            'ad_groups': {},      # {('campaña', 'grupo'): id_grupo}
            'ads': {},           # {('campaña', 'grupo', 'ad_key'): id_anuncio}
            'keywords': {}       # {('campaña', 'grupo', 'palabra'): id_palabra}
        }
        
        print("🔗 Detectando relaciones jerárquicas...")
        
        # Buscar columnas de campaña y grupo de anuncios
        campaign_col = None
        ad_group_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ['campaign', 'campaña']) and not campaign_col:
                campaign_col = col
            elif any(term in col_lower for term in ['ad group', 'grupo', 'adgroup']) and not ad_group_col:
                ad_group_col = col
        
        print(f"📊 Columna de campaña detectada: {campaign_col}")
        print(f"📊 Columna de grupo de anuncios detectada: {ad_group_col}")
        
        # Generar IDs únicos para campañas
        if campaign_col and campaign_col in df.columns:
            unique_campaigns = df[campaign_col].dropna().unique()
            for i, campaign in enumerate(unique_campaigns, 1):
                if campaign and str(campaign).strip():
                    relationships['campaigns'][str(campaign).strip()] = i
            print(f"🎯 {len(relationships['campaigns'])} campañas únicas detectadas")
        
        # Generar IDs únicos para grupos de anuncios
        if campaign_col and ad_group_col and campaign_col in df.columns and ad_group_col in df.columns:
            unique_groups = df[[campaign_col, ad_group_col]].dropna().drop_duplicates()
            for i, (_, row) in enumerate(unique_groups.iterrows(), 1):
                campaign = str(row[campaign_col]).strip() if row[campaign_col] else ""
                ad_group = str(row[ad_group_col]).strip() if row[ad_group_col] else ""
                if campaign and ad_group:
                    relationships['ad_groups'][(campaign, ad_group)] = i
            print(f"📂 {len(relationships['ad_groups'])} grupos de anuncios únicos detectados")
        
        # Para anuncios y palabras clave, generar IDs basados en contenido único
        if self.table_type == 'anuncios':
            # Buscar columna identificativa de anuncio
            ad_identifier_cols = ['titulo_1', 'headline_1', 'headline 1', 'Headline 1', 'ad_type', 'tipo_anuncio', 'url_final', 'Final URL']
            ad_id_col = None
            for col in ad_identifier_cols:
                if col in df.columns:
                    ad_id_col = col
                    break
            
            print(f"📺 Columna identificativa de anuncio detectada: {ad_id_col}")
            
            if ad_id_col and campaign_col and ad_group_col:
                unique_ads = df[[campaign_col, ad_group_col, ad_id_col]].dropna().drop_duplicates()
                for i, (_, row) in enumerate(unique_ads.iterrows(), 1):
                    campaign = str(row[campaign_col]).strip() if row[campaign_col] else ""
                    ad_group = str(row[ad_group_col]).strip() if row[ad_group_col] else ""
                    ad_key = str(row[ad_id_col]).strip() if row[ad_id_col] else ""
                    if campaign and ad_group and ad_key:
                        relationships['ads'][(campaign, ad_group, ad_key)] = i
                print(f"📺 {len(relationships['ads'])} anuncios únicos detectados")
        
        elif self.table_type == 'palabras_clave':
            # Buscar columna de palabra clave
            keyword_col = None
            for col in df.columns:
                col_lower = col.lower()
                if any(term in col_lower for term in ['keyword', 'palabra', 'clave']) and not keyword_col:
                    keyword_col = col
                    break
            
            print(f"🔑 Columna de palabra clave detectada: {keyword_col}")
            
            if keyword_col and campaign_col and ad_group_col:
                unique_keywords = df[[campaign_col, ad_group_col, keyword_col]].dropna().drop_duplicates()
                for i, (_, row) in enumerate(unique_keywords.iterrows(), 1):
                    campaign = str(row[campaign_col]).strip() if row[campaign_col] else ""
                    ad_group = str(row[ad_group_col]).strip() if row[ad_group_col] else ""
                    keyword = str(row[keyword_col]).strip() if row[keyword_col] else ""
                    if campaign and ad_group and keyword:
                        relationships['keywords'][(campaign, ad_group, keyword)] = i
                print(f"🔑 {len(relationships['keywords'])} palabras clave únicas detectadas")
        
        return relationships
    
    def assign_relational_ids(self, df: pd.DataFrame, relationships: Dict) -> pd.DataFrame:
        """Asigna IDs relacionales al DataFrame basado en las relaciones detectadas"""
        
        print("🔗 Asignando IDs relacionales...")
        
        # Buscar columnas relevantes
        campaign_col = None
        ad_group_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ['campaign', 'campaña']) and not campaign_col:
                campaign_col = col
            elif any(term in col_lower for term in ['ad group', 'grupo', 'adgroup']) and not ad_group_col:
                ad_group_col = col
        
        # Asignar ID de campaña
        if campaign_col and 'id_campaña' in self.target_columns:
            df['id_campaña'] = df[campaign_col].apply(
                lambda x: relationships['campaigns'].get(str(x).strip() if x else "", None)
            )
            print(f"✅ IDs de campaña asignados: {df['id_campaña'].notna().sum()} registros")
        
        # Asignar ID de grupo de anuncios
        if campaign_col and ad_group_col and 'id_grupo_anuncios' in self.target_columns:
            def get_ad_group_id(row):
                campaign = str(row[campaign_col]).strip() if row[campaign_col] else ""
                ad_group = str(row[ad_group_col]).strip() if row[ad_group_col] else ""
                return relationships['ad_groups'].get((campaign, ad_group), None)
            
            df['id_grupo_anuncios'] = df.apply(get_ad_group_id, axis=1)
            print(f"✅ IDs de grupo de anuncios asignados: {df['id_grupo_anuncios'].notna().sum()} registros")
        
        # Asignar IDs específicos según el tipo de tabla
        if self.table_type == 'anuncios' and 'id_anuncio' in self.target_columns:
            # Buscar columna identificativa de anuncio
            ad_identifier_cols = ['titulo_1', 'headline_1', 'headline 1', 'Headline 1', 'ad_type', 'tipo_anuncio', 'url_final', 'Final URL']
            ad_id_col = None
            for col in ad_identifier_cols:
                if col in df.columns:
                    ad_id_col = col
                    break
            
            print(f"📺 Columna para ID de anuncio: {ad_id_col}")
            
            if ad_id_col:
                def get_ad_id(row):
                    campaign = str(row[campaign_col]).strip() if campaign_col and row[campaign_col] else ""
                    ad_group = str(row[ad_group_col]).strip() if ad_group_col and row[ad_group_col] else ""
                    ad_key = str(row[ad_id_col]).strip() if row[ad_id_col] else ""
                    return relationships['ads'].get((campaign, ad_group, ad_key), None)
                
                df['id_anuncio'] = df.apply(get_ad_id, axis=1)
                print(f"✅ IDs de anuncio asignados: {df['id_anuncio'].notna().sum()} registros")
        
        elif self.table_type == 'palabras_clave' and 'id_palabra_clave' in self.target_columns:
            # Buscar columna de palabra clave después del mapeo
            keyword_cols_mapped = ['palabra_clave', 'keyword']
            keyword_col = None
            for col in keyword_cols_mapped:
                if col in df.columns:
                    keyword_col = col
                    break
            
            print(f"🔑 Columna para ID de palabra clave: {keyword_col}")
            
            if keyword_col:
                def get_keyword_id(row):
                    campaign = str(row[campaign_col]).strip() if campaign_col and row[campaign_col] else ""
                    ad_group = str(row[ad_group_col]).strip() if ad_group_col and row[ad_group_col] else ""
                    keyword = str(row[keyword_col]).strip() if row[keyword_col] else ""
                    return relationships['keywords'].get((campaign, ad_group, keyword), None)
                
                df['id_palabra_clave'] = df.apply(get_keyword_id, axis=1)
                print(f"✅ IDs de palabra clave asignados: {df['id_palabra_clave'].notna().sum()} registros")
        
        return df
def main():
    """Función principal para ejecutar el script"""
    
    print("🎯 GENERADOR DE SQL PARA GOOGLE ADS - SUPABASE")
    print("=" * 60)
    
    # Verificar que existe la API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: No se encontró OPENAI_API_KEY en las variables de entorno")
        print("📝 Asegúrate de configurar tu API key en el archivo .env")
        return
    
    # Inicializar analizador
    analyzer = GoogleAdsExcelAnalyzer()
    
    # Solicitar archivo Excel
    excel_file = input("\n📁 Ingresa la ruta del archivo Excel: ").strip()
    
    if not os.path.exists(excel_file):
        print(f"❌ Error: No se encontró el archivo {excel_file}")
        return
    
    # Preguntar por la hoja (opcional)
    sheet_name = input("📋 Nombre de la hoja (Enter para usar la primera): ").strip()
    if not sheet_name:
        sheet_name = None
    
    # Archivo de salida
    output_file = input("💾 Nombre del archivo SQL de salida (Enter para 'google_ads_inserts.sql'): ").strip()
    if not output_file:
        output_file = "google_ads_inserts.sql"
    
    # Procesar
    result = analyzer.process_excel_to_sql(excel_file, output_file, sheet_name)
    
    if result['success']:
        print(f"\n🎉 ¡Éxito! Tu archivo SQL está listo: {result['output_file']}")
        print("\n📋 SIGUIENTES PASOS:")
        print("1. Revisa el archivo SQL generado")
        print("2. Ejecuta las sentencias en tu base de datos Supabase")
        print("3. Verifica que los datos se insertaron correctamente")
    else:
        print(f"\n💥 Error durante el proceso: {result['error']}")


if __name__ == "__main__":
    main()
