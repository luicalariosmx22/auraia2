import pandas as pd
import os
import re
from typing import List, Optional

class SimpleExcelToSQL:
    """Versión simplificada sin IA para mapeo manual rápido"""
    
    def __init__(self):
        # Columnas para anuncios incluyendo relaciones jerárquicas
        self.target_columns = [
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
            # Columnas de relación para mantener jerarquía
            'id_campaña', 'id_grupo_anuncios', 'id_anuncio'
        ]

    def create_manual_mapping(self, excel_columns: List[str]) -> dict:
        """Crea un mapeo manual común para archivos de Google Ads"""
        
        # Mapeos comunes de Google Ads a nuestra tabla
        common_mappings = {
            # Estados y URLs
            'Ad state': 'estado_anuncio',
            'Estado del anuncio': 'estado_anuncio',
            'Final URL': 'url_final',
            'URL final': 'url_final',
            'Mobile final URL': 'url_final_movil',
            'URL final móvil': 'url_final_movil',
            
            # Títulos (buscar patrones)
            'Headline 1': 'titulo_1',
            'Headline 2': 'titulo_2',
            'Headline 3': 'titulo_3',
            'Título 1': 'titulo_1',
            'Título 2': 'titulo_2',
            'Título 3': 'titulo_3',
            
            # Descripciones
            'Description 1': 'descripcion_1',
            'Description 2': 'descripcion_2',
            'Descripción 1': 'descripcion_1',
            'Descripción 2': 'descripcion_2',
            
            # Rutas
            'Path 1': 'ruta_1',
            'Path 2': 'ruta_2',
            'Ruta 1': 'ruta_1',
            'Ruta 2': 'ruta_2',
            
            # Campaña y grupo
            'Campaign': 'campaña',
            'Campaña': 'campaña',
            'Campaign ID': 'id_campaña',
            'ID de campaña': 'id_campaña',
            'Ad group': 'grupo_anuncios',
            'Grupo de anuncios': 'grupo_anuncios',
            'Ad group ID': 'id_grupo_anuncios',
            'ID del grupo de anuncios': 'id_grupo_anuncios',
            'Ad ID': 'id_anuncio',
            'ID del anuncio': 'id_anuncio',
            
            # Estado general
            'Status': 'estado',
            'Estado': 'estado',
            'State': 'estado',
            
            # Métricas
            'Clicks': 'clics',
            'Clics': 'clics',
            'Impressions': 'impresiones',
            'Impresiones': 'impresiones',
            'CTR': 'ctr',
            'Avg. CPC': 'cpc_promedio',
            'CPC promedio': 'cpc_promedio',
            'Cost': 'costo',
            'Costo': 'costo',
            'Conv. rate': 'porcentaje_conversion',
            'Tasa de conversión': 'porcentaje_conversion',
            'Conversions': 'conversiones',
            'Conversiones': 'conversiones',
            'Cost / conv.': 'costo_por_conversion',
            'Costo por conversión': 'costo_por_conversion',
            'Currency': 'codigo_moneda',
            'Moneda': 'codigo_moneda'
        }
        
        # Crear mapeo final
        mapping = {}
        for excel_col in excel_columns:
            if excel_col in common_mappings:
                mapping[excel_col] = common_mappings[excel_col]
            else:
                # Buscar coincidencias parciales para títulos numerados
                for i in range(1, 16):
                    if f"headline {i}" in excel_col.lower() or f"título {i}" in excel_col.lower():
                        mapping[excel_col] = f'titulo_{i}'
                        break
                    elif f"headline {i} position" in excel_col.lower():
                        mapping[excel_col] = f'pos_titulo_{i}'
                        break
                
                # Buscar descripciones
                for i in range(1, 5):
                    if f"description {i}" in excel_col.lower() or f"descripción {i}" in excel_col.lower():
                        mapping[excel_col] = f'descripcion_{i}'
                        break
                    elif f"description {i} position" in excel_col.lower():
                        mapping[excel_col] = f'pos_desc_{i}'
                        break
        
        return mapping

    def process_excel_simple(self, excel_file: str, output_file: str = "google_ads_simple.sql", sheet_name: Optional[str] = None, table_type: str = 'anuncios'):
        """Proceso simplificado sin IA"""
        
        print("🚀 Procesando Excel con mapeo automático...")
        print(f"📁 Archivo de entrada: {excel_file}")
        print(f"📁 Archivo de salida: {output_file}")
        print(f"📁 Tipo de tabla: {table_type}")
        print(f"📁 Hoja: {sheet_name}")
        print(f"📁 Archivo existe: {os.path.exists(excel_file)}")
        
        # Si es tabla de palabras clave, usar el generador específico
        if table_type == 'palabras_clave':
            print("🔑 Delegando a KeywordsGenerator...")
            try:
                from keywords_generator import KeywordsExcelToSQL
                keywords_gen = KeywordsExcelToSQL()
                return keywords_gen.process_excel_to_sql(excel_file, output_file, sheet_name)
            except Exception as e:
                print(f"❌ Error importando keywords_generator: {e}")
                return False
        
        # Si es tabla de campañas, usar el generador específico
        if table_type == 'campañas':
            print("📈 Delegando a CampaignsGenerator...")
            try:
                from campaigns_generator import CampaignsExcelToSQL
                campaigns_gen = CampaignsExcelToSQL()
                return campaigns_gen.process_excel_to_sql(excel_file, output_file, sheet_name)
            except Exception as e:
                print(f"❌ Error importando campaigns_generator: {e}")
                return False
        
        # Continuar con lógica existente para anuncios
        print("📢 Procesando como tabla de anuncios...")
        
        try:
            # Leer Excel
            print("📖 Leyendo archivo Excel...")
            if sheet_name:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_file)
            print(f"📊 Archivo leído: {df.shape[0]} filas, {df.shape[1]} columnas")
            print(f"🔍 Columnas encontradas: {list(df.columns)}")
            
            # Limpiar columnas innecesarias
            print("🧹 Limpiando columnas innecesarias...")
            df = self._clean_unnamed_columns(df)
            print(f"📊 Columnas después de limpieza: {df.shape[1]}")
            
            # Crear mapeo automático
            print("🗺️ Creando mapeo automático...")
            mapping = self.create_manual_mapping(list(df.columns))
            print(f"🔄 Mapeos encontrados: {len(mapping)}")
            
            # Mostrar mapeos
            if mapping:
                print("\n📋 MAPEOS APLICADOS:")
                for excel_col, target_col in mapping.items():
                    print(f"  '{excel_col}' → '{target_col}'")
            else:
                print("⚠️ ADVERTENCIA: No se encontraron mapeos automáticos")
            
            # Crear DataFrame final
            print("🏗️ Construyendo DataFrame final...")
            final_df = pd.DataFrame()
            
            # Aplicar mapeos
            mapped_count = 0
            for excel_col, target_col in mapping.items():
                if excel_col in df.columns:
                    final_df[target_col] = df[excel_col]
                    mapped_count += 1
                    print(f"  ✅ Mapeado: '{excel_col}' → '{target_col}'")
            
            print(f"📊 Columnas mapeadas exitosamente: {mapped_count}")
            
            # Completar columnas faltantes
            missing_cols = 0
            for col in self.target_columns:
                if col not in final_df.columns:
                    final_df[col] = None
                    missing_cols += 1
            
            print(f"📝 Columnas completadas con NULL: {missing_cols}")
            print(f"📋 Total columnas en tabla destino: {len(self.target_columns)}")
            
            # Reordenar
            final_df = final_df[self.target_columns]
            print(f"🔢 DataFrame final reordenado: {final_df.shape}")
            
            # Limpiar datos
            print("🧹 Limpiando y validando datos...")
            for col in final_df.columns:
                final_df[col] = final_df[col].astype(str).replace('nan', '').replace('None', '')
                final_df[col] = final_df[col].str.replace("'", "''")
                final_df[col] = final_df[col].replace('', None)
            
            print("✅ Datos limpiados")
            
            # Generar SQL
            print("📝 Generando sentencias SQL...")
            sql_statements = []
            for index, row in final_df.iterrows():
                values = []
                for col in self.target_columns:
                    value = row[col]
                    if pd.isna(value) or value is None or value == '':
                        values.append('NULL')
                    else:
                        values.append(f"'{str(value)}'")
                
                values_str = ', '.join(values)
                sql = f"""INSERT INTO public.google_ads_reporte_anuncios (
    {', '.join(self.target_columns)}
) VALUES (
    {values_str}
);"""
                sql_statements.append(sql)
            
            print(f"📊 Sentencias SQL generadas: {len(sql_statements)}")
            
            # Guardar archivo
            print(f"💾 Guardando archivo SQL: {output_file}")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("-- SQL generado automáticamente (versión simple)\n")
                f.write(f"-- Archivo fuente: {excel_file}\n")
                f.write(f"-- Fecha: {pd.Timestamp.now()}\n")
                f.write(f"-- Registros procesados: {len(sql_statements)}\n\n")
                
                for i, sql in enumerate(sql_statements, 1):
                    f.write(f"-- Registro {i}\n")
                    f.write(sql)
                    f.write("\n\n")
            
            print(f"✅ Proceso completado exitosamente!")
            print(f"📊 Resultado: {len(sql_statements)} registros → {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error en process_excel_simple: {str(e)}")
            import traceback
            print(f"🔍 Traceback completo:")
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


def main_simple():
    """Función principal para el proceso simple"""
    print("🎯 GENERADOR SQL SIMPLE - GOOGLE ADS")
    print("=" * 50)
    
    converter = SimpleExcelToSQL()
    
    excel_file = input("📁 Ruta del archivo Excel: ").strip()
    if not os.path.exists(excel_file):
        print(f"❌ Archivo no encontrado: {excel_file}")
        return
    
    output_file = input("💾 Archivo SQL de salida (Enter para 'google_ads_simple.sql'): ").strip()
    if not output_file:
        output_file = "google_ads_simple.sql"
    
    success = converter.process_excel_simple(excel_file, output_file)
    
    if success:
        print(f"\n🎉 ¡Archivo SQL generado exitosamente: {output_file}!")
    else:
        print("\n💥 Error durante el proceso")


if __name__ == "__main__":
    main_simple()
