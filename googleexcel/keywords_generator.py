import pandas as pd
import os
import re
from typing import List, Optional, Dict

class KeywordsExcelToSQL:
    """Generador específico para la tabla google_ads_palabras_clave"""
    
    def __init__(self):
        # Columnas para palabras clave incluyendo relaciones jerárquicas  
        self.target_columns = [
            'estado_palabra_clave',
            'palabra_clave',
            'tipo_concordancia',
            'campaña',
            'grupo_anuncios',
            'estado',
            'motivos_estado',
            'url_final',
            'url_final_movil',
            'impresiones',
            'ctr',
            'codigo_moneda',
            'costo',
            'clics',
            'porcentaje_conversion',
            'conversiones',
            'cpc_promedio',
            'costo_por_conversion',
            # Columnas de relación para mantener jerarquía
            'id_campaña',
            'id_grupo_anuncios',
            'id_palabra_clave'
        ]
        
        # Mapeos comunes de Google Ads a nuestra tabla (basado en las 18 columnas exactas)
        self.common_mappings = {
            # Campaña y grupo
            'Campaign': 'campaña',
            'Campaña': 'campaña',
            'Campaign name': 'campaña',
            'Nombre de campaña': 'campaña',
            'Ad group': 'grupo_anuncios',
            'Grupo de anuncios': 'grupo_anuncios',
            'Ad group name': 'grupo_anuncios',
            'Nombre del grupo de anuncios': 'grupo_anuncios',
            
            # Palabra clave
            'Keyword': 'palabra_clave',
            'Palabra clave': 'palabra_clave',
            'Keywords': 'palabra_clave',
            'Palabras clave': 'palabra_clave',
            
            # Estados
            'Keyword state': 'estado_palabra_clave',
            'Estado de palabra clave': 'estado_palabra_clave',
            'Status': 'estado',
            'Estado': 'estado',
            'Approval status': 'motivos_estado',
            'Estado de aprobación': 'motivos_estado',
            
            # Tipo de concordancia
            'Match type': 'tipo_concordancia',
            'Tipo de concordancia': 'tipo_concordancia',
            
            # URLs
            'Final URL': 'url_final',
            'URL final': 'url_final',
            'Mobile final URL': 'url_final_movil',
            'URL final móvil': 'url_final_movil',
            'URL final para celulares': 'url_final_movil',
            
            # Moneda
            'Currency code': 'codigo_moneda',
            'Código de moneda': 'codigo_moneda',
            
            # Métricas de rendimiento
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
            'Conversions': 'conversiones',
            'Conversiones': 'conversiones',
            'Cost/conv.': 'costo_por_conversion',
            'Costo/conv.': 'costo_por_conversion',
            'Conv. rate': 'porcentaje_conversion',
            'Porcentaje de conversión': 'porcentaje_conversion',
            'Porcentaje de conv.': 'porcentaje_conversion'
        }

    def create_mapping(self, excel_columns: List[str]) -> Dict[str, str]:
        """Crea un mapeo de columnas de Excel a columnas de la tabla"""
        mapping = {}
        
        # Aplicar mapeos comunes
        for excel_col in excel_columns:
            excel_col_clean = excel_col.strip()
            if excel_col_clean in self.common_mappings:
                mapping[excel_col_clean] = self.common_mappings[excel_col_clean]
        
        print(f"=== MAPEO KEYWORDS ===")
        print(f"Columnas encontradas: {len(excel_columns)}")
        print(f"Mapeos aplicados: {len(mapping)}")
        for excel_col, db_col in mapping.items():
            print(f"  {excel_col} -> {db_col}")
        
        return mapping

    def clean_value(self, value, column_name: str) -> str:
        """Limpia y formatea valores según el tipo de columna"""
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return 'NULL'
        
        value_str = str(value).strip()
        
        # Columnas numéricas que pueden ser NULL
        numeric_columns = [
            'impresiones', 'clics', 'ctr', 'cpc_promedio', 'costo', 'conversiones',
            'costo_por_conversion', 'porcentaje_conversion'
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
        table_name = "public.google_ads_palabras_clave"
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
        
        # Patrones específicos para detectar cabeceras como datos
        header_patterns = [
            'estado de palabras clave',
            'palabra clave',
            'tipo de concordancia',
            'tipo concordancia',
            'match type',
            'keyword',
            'campaign',
            'campaña',
            'ad group',
            'grupo de anuncios',
            'grupo anuncios',
            'impresiones',
            'impressions',
            'clicks',
            'clics',
            'habilitado',  # ⭐ Agregar "habilitado" como patrón problemático
            'enabled',
            'paused',
            'pausado',
            'estado',
            'status'
        ]
        
        # Buscar en todas las columnas de texto para identificar filas de resumen
        mask_to_keep = pd.Series([True] * len(df_filtered))
        
        for col in df_filtered.columns:
            if df_filtered[col].dtype == 'object':  # Solo columnas de texto
                # Filtrar patrones de resumen
                for pattern in summary_patterns:
                    pattern_mask = ~df_filtered[col].astype(str).str.lower().str.contains(pattern, na=False)
                    mask_to_keep = mask_to_keep & pattern_mask
                
                # Filtrar patrones de cabeceras (especialmente para la columna de palabra clave)
                if 'palabra' in col.lower() or 'keyword' in col.lower():
                    for header_pattern in header_patterns:
                        header_mask = ~(df_filtered[col].astype(str).str.lower() == header_pattern.lower())
                        mask_to_keep = mask_to_keep & header_mask
        
        # Aplicar filtro
        df_filtered = df_filtered[mask_to_keep]
        
        # Filtro adicional: eliminar filas donde todas las columnas importantes están vacías
        important_cols = ['palabra_clave', 'campaña', 'grupo_anuncios']
        available_important_cols = [col for col in important_cols if col in df_filtered.columns]
        
        if available_important_cols:
            # Mantener solo filas que tienen al menos una columna importante con datos
            has_data_mask = df_filtered[available_important_cols].notna().any(axis=1)
            df_filtered = df_filtered[has_data_mask]
        
        print(f"📊 Filas después del filtrado: {len(df_filtered)}")
        print(f"🗑️ Filas de totales eliminadas: {len(df) - len(df_filtered)}")
        
        # Debug: Mostrar las primeras palabras clave para verificar
        if len(df_filtered) > 0 and 'palabra_clave' in df_filtered.columns:
            print(f"🔍 Primeras 3 palabras clave después del filtro:")
            sample_keywords = df_filtered['palabra_clave'].dropna().head(3).tolist()
            for i, kw in enumerate(sample_keywords):
                print(f"   {i+1}. '{kw}'")
        
        return df_filtered

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

    def process_excel_to_sql(self, excel_file: str, output_file: str, sheet_name: Optional[str] = None) -> bool:
        """Procesa un archivo Excel y genera SQL para palabras clave"""
        try:
            print(f"=== KEYWORDS PROCESSOR ===")
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
                print("❌ ERROR: No se encontraron palabras clave válidas después del filtrado")
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
            
            # Agregar columnas faltantes con NULL
            for col in self.target_columns:
                if col not in df_mapped.columns:
                    df_mapped[col] = None
                    print(f"Columna faltante rellenada con NULL: {col}")
            
            # Reordenar columnas según el orden de la tabla
            df_mapped = df_mapped[self.target_columns]
            
            print(f"DataFrame final: {len(df_mapped)} filas, {len(df_mapped.columns)} columnas")
            
            # Generar SQL
            sql_statements = self.generate_insert_sql(df_mapped)
            
            # Escribir archivo
            output_dir = os.path.dirname(output_file)
            if output_dir:  # Solo crear directorio si hay uno
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Escribir encabezado
                f.write("-- SQL generado para google_ads_palabras_clave\n")
                f.write(f"-- Archivo origen: {os.path.basename(excel_file)}\n")
                f.write(f"-- Registros: {len(sql_statements)}\n")
                f.write(f"-- Generado: {pd.Timestamp.now()}\n\n")
                
                # Escribir sentencias SQL
                for sql in sql_statements:
                    f.write(sql + '\n')
            
            print(f"✅ SQL generado exitosamente: {len(sql_statements)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Error procesando keywords: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False


def test_keywords_generator():
    """Función de prueba para el generador de keywords"""
    # Crear datos de ejemplo
    test_data = {
        'Campaign': ['Campaña Test 1', 'Campaña Test 2'],
        'Ad group': ['Grupo 1', 'Grupo 2'],
        'Keyword': ['marketing digital', 'publicidad online'],
        'Match type': ['Exact', 'Broad'],
        'Keyword state': ['Enabled', 'Enabled'],
        'Max CPC': [1.50, 2.00],
        'Impressions': [1000, 1500],
        'Clicks': [50, 75],
        'CTR': [5.0, 5.0],
        'Cost': [75.0, 150.0]
    }
    
    df = pd.DataFrame(test_data)
    
    # Crear archivo Excel temporal
    test_excel = 'test_keywords.xlsx'
    df.to_excel(test_excel, index=False)
    
    # Procesar
    generator = KeywordsExcelToSQL()
    success = generator.process_excel_to_sql(test_excel, 'test_keywords_output.sql')
    
    # Limpiar
    if os.path.exists(test_excel):
        os.remove(test_excel)
    
    return success


if __name__ == "__main__":
    print("🔑 Testing Keywords Generator...")
    success = test_keywords_generator()
    print(f"Test result: {'✅ Success' if success else '❌ Failed'}")
