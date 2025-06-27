"""
Cliente de Supabase para insertar datos de Google Ads manteniendo relaciones jerárquicas
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Optional
import pandas as pd
import json
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

class SupabaseGoogleAdsClient:
    """Cliente para manejar inserciones en Supabase con relaciones jerárquicas"""
    
    def __init__(self):
        """Inicializa el cliente de Supabase"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Error: SUPABASE_URL y SUPABASE_ANON_KEY deben estar configuradas en .env")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Cliente de Supabase inicializado correctamente")
        except TypeError as e:
            if 'proxy' in str(e):
                # Si el error es por el argumento proxy, intentar inicializar sin opciones adicionales
                from supabase import Client as SupabaseClient
                self.supabase = SupabaseClient(self.supabase_url, self.supabase_key)
                print("✅ Cliente de Supabase inicializado en modo compatible")
            else:
                raise
    
    def test_connection(self) -> Dict:
        """Prueba la conexión a Supabase"""
        try:
            # Intentar hacer una consulta simple
            result = self.supabase.table('google_ads_campañas').select('id_campaña').limit(1).execute()
            return {
                'success': True,
                'message': 'Conexión a Supabase exitosa',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_all_tables(self) -> Dict:
        """Limpia todas las tablas de Google Ads (CUIDADO: borra todos los datos)"""
        try:
            # Orden correcto para borrar (por dependencias FK)
            tables = ['google_ads_palabras_clave', 'google_ads_reporte_anuncios', 'google_ads_campañas']
            deleted_counts = {}
            
            for table in tables:
                deleted_counts[table] = self._force_clear_table(table)
            
            return {
                'success': True,
                'message': 'Tablas limpiadas exitosamente',
                'deleted_counts': deleted_counts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error limpiando tablas: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _force_clear_table(self, table_name: str) -> int:
        """Fuerza el borrado completo de una tabla sin importar su estructura"""
        try:
            print(f"🔍 Analizando tabla {table_name}...")
            
            # Primer intento: contar registros existentes
            count_result = self.supabase.table(table_name).select('*', count='exact').execute()
            initial_count = count_result.count if hasattr(count_result, 'count') else 0
            
            if initial_count == 0:
                print(f"✅ {table_name}: Ya estaba vacía")
                return 0
            
            print(f"📊 {table_name}: {initial_count} registros encontrados")
            
            # Estrategia 1: Intentar con created_at
            try:
                result = self.supabase.table(table_name).delete().gte('created_at', '1900-01-01').execute()
                if result.data and len(result.data) > 0:
                    print(f"🗑️ {table_name}: {len(result.data)} registros eliminados (método created_at)")
                    return len(result.data)
            except Exception as e:
                print(f"⚠️ Método created_at falló en {table_name}: {str(e)}")
            
            # Estrategia 2: Intentar con id
            try:
                result = self.supabase.table(table_name).delete().gte('id', 0).execute()
                if result.data and len(result.data) > 0:
                    print(f"🗑️ {table_name}: {len(result.data)} registros eliminados (método id)")
                    return len(result.data)
            except Exception as e:
                print(f"⚠️ Método id falló en {table_name}: {str(e)}")
            
            # Estrategia 3: Obtener esquema y usar primera columna
            try:
                # Obtener un registro de muestra para ver la estructura
                sample = self.supabase.table(table_name).select('*').limit(1).execute()
                if sample.data and len(sample.data) > 0:
                    first_field = list(sample.data[0].keys())[0]
                    print(f"🔧 Usando campo '{first_field}' para limpiar {table_name}")
                    result = self.supabase.table(table_name).delete().is_('id', None).execute()
                    if not result.data:
                        # Si no hay datos en result, intentar otra condición
                        result = self.supabase.table(table_name).delete().neq(first_field, '___IMPOSSIBLE_VALUE___').execute()
                    
                    if result.data and len(result.data) > 0:
                        print(f"🗑️ {table_name}: {len(result.data)} registros eliminados (método campo '{first_field}')")
                        return len(result.data)
            except Exception as e:
                print(f"⚠️ Método esquema falló en {table_name}: {str(e)}")
            
            # Estrategia 4: Borrado por lotes usando select + delete individual
            try:
                print(f"🔄 Intentando borrado por lotes en {table_name}...")
                all_records = self.supabase.table(table_name).select('*').execute()
                if all_records.data and len(all_records.data) > 0:
                    deleted_count = 0
                    # Obtener el campo clave primaria
                    first_record = all_records.data[0]
                    pk_candidates = ['id', 'id_campaña', 'id_anuncio', 'id_palabra_clave']
                    pk_field = None
                    
                    for candidate in pk_candidates:
                        if candidate in first_record:
                            pk_field = candidate
                            break
                    
                    if not pk_field:
                        pk_field = list(first_record.keys())[0]
                    
                    print(f"🔑 Usando '{pk_field}' como clave para borrado en {table_name}")
                    
                    # Borrar en lotes de 100
                    batch_size = 100
                    for i in range(0, len(all_records.data), batch_size):
                        batch = all_records.data[i:i + batch_size]
                        pk_values = [record[pk_field] for record in batch]
                        
                        try:
                            batch_result = self.supabase.table(table_name).delete().in_(pk_field, pk_values).execute()
                            if batch_result.data:
                                deleted_count += len(batch_result.data)
                            print(f"� Lote {i//batch_size + 1}: {len(batch_result.data) if batch_result.data else 0} registros eliminados")
                        except Exception as batch_error:
                            print(f"❌ Error en lote {i//batch_size + 1}: {str(batch_error)}")
                    
                    if deleted_count > 0:
                        print(f"🗑️ {table_name}: {deleted_count} registros eliminados (método por lotes)")
                        return deleted_count
            except Exception as e:
                print(f"⚠️ Método por lotes falló en {table_name}: {str(e)}")
            
            # Estrategia 5: Verificar si realmente está vacía
            try:
                final_count = self.supabase.table(table_name).select('*', count='exact').execute()
                final_total = final_count.count if hasattr(final_count, 'count') else 0
                if final_total == 0:
                    print(f"✅ {table_name}: Confirmado vacía tras intentos de limpieza")
                    return initial_count  # Asumimos que se limpiaron todos
                else:
                    print(f"⚠️ {table_name}: Aún contiene {final_total} registros")
                    return initial_count - final_total
            except Exception as e:
                print(f"❌ Error verificando estado final de {table_name}: {str(e)}")
            
            print(f"❌ No se pudo limpiar completamente {table_name}")
            return 0
            
        except Exception as e:
            print(f"❌ Error crítico limpiando {table_name}: {str(e)}")
            return 0
    
    def insert_campaigns(self, campaigns_data: List[Dict]) -> Dict:
        """Inserta campañas en Supabase"""
        try:
            print(f"📈 Insertando {len(campaigns_data)} campañas...")
            
            # Limpiar datos y preparar para inserción
            clean_campaigns = []
            for campaign in campaigns_data:
                clean_campaign = self._clean_data_for_supabase(campaign)
                clean_campaigns.append(clean_campaign)
            
            # Insertar en lotes para evitar límites de Supabase
            batch_size = 100
            inserted_count = 0
            
            for i in range(0, len(clean_campaigns), batch_size):
                batch = clean_campaigns[i:i + batch_size]
                result = self.supabase.table('google_ads_campañas').insert(batch).execute()
                inserted_count += len(result.data) if result.data else 0
                print(f"📈 Lote {i//batch_size + 1}: {len(result.data) if result.data else 0} campañas insertadas")
            
            return {
                'success': True,
                'message': f'{inserted_count} campañas insertadas exitosamente',
                'inserted_count': inserted_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error insertando campañas: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def insert_ads(self, ads_data: List[Dict]) -> Dict:
        """Inserta anuncios en Supabase"""
        try:
            print(f"📺 Insertando {len(ads_data)} anuncios...")
            
            # Limpiar datos y preparar para inserción
            clean_ads = []
            for ad in ads_data:
                clean_ad = self._clean_data_for_supabase(ad)
                clean_ads.append(clean_ad)
            
            # Insertar en lotes
            batch_size = 100
            inserted_count = 0
            
            for i in range(0, len(clean_ads), batch_size):
                batch = clean_ads[i:i + batch_size]
                result = self.supabase.table('google_ads_reporte_anuncios').insert(batch).execute()
                inserted_count += len(result.data) if result.data else 0
                print(f"📺 Lote {i//batch_size + 1}: {len(result.data) if result.data else 0} anuncios insertados")
            
            return {
                'success': True,
                'message': f'{inserted_count} anuncios insertados exitosamente',
                'inserted_count': inserted_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error insertando anuncios: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def insert_keywords(self, keywords_data: List[Dict]) -> Dict:
        """Inserta palabras clave en Supabase"""
        try:
            print(f"🔑 Insertando {len(keywords_data)} palabras clave...")
            
            # Limpiar datos y preparar para inserción
            clean_keywords = []
            for keyword in keywords_data:
                clean_keyword = self._clean_data_for_supabase(keyword)
                clean_keywords.append(clean_keyword)
            
            # Insertar en lotes
            batch_size = 100
            inserted_count = 0
            
            for i in range(0, len(clean_keywords), batch_size):
                batch = clean_keywords[i:i + batch_size]
                result = self.supabase.table('google_ads_palabras_clave').insert(batch).execute()
                inserted_count += len(result.data) if result.data else 0
                print(f"🔑 Lote {i//batch_size + 1}: {len(result.data) if result.data else 0} palabras clave insertadas")
            
            return {
                'success': True,
                'message': f'{inserted_count} palabras clave insertadas exitosamente',
                'inserted_count': inserted_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error insertando palabras clave: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def insert_all_data(self, campaigns_file: str, ads_file: str, keywords_file: str, clear_tables: bool = True) -> Dict:
        """Inserta todos los datos en el orden correcto para mantener relaciones"""
        try:
            print("🚀 INICIANDO INSERCIÓN COMPLETA A SUPABASE")
            print("=" * 50)
            
            # 1. Limpiar tablas si se solicita
            if clear_tables:
                print("🗑️ Limpiando tablas existentes...")
                clear_result = self.clear_all_tables()
                if not clear_result['success']:
                    return clear_result
            
            # 2. Procesar archivos SQL y extraer datos
            campaigns_data = self._parse_sql_file(campaigns_file)
            ads_data = self._parse_sql_file(ads_file)
            keywords_data = self._parse_sql_file(keywords_file)
            
            print(f"📊 Datos extraídos:")
            print(f"  📈 Campañas: {len(campaigns_data)}")
            print(f"  📺 Anuncios: {len(ads_data)}")
            print(f"  🔑 Palabras clave: {len(keywords_data)}")
            
            results = {}
            
            # 3. Insertar en orden jerárquico
            print("\n📈 PASO 1: Insertando campañas...")
            campaigns_result = self.insert_campaigns(campaigns_data)
            results['campaigns'] = campaigns_result
            
            if not campaigns_result['success']:
                return {
                    'success': False,
                    'error': f"Error en campañas: {campaigns_result['error']}",
                    'results': results
                }
            
            print("\n📺 PASO 2: Insertando anuncios...")
            ads_result = self.insert_ads(ads_data)
            results['ads'] = ads_result
            
            if not ads_result['success']:
                return {
                    'success': False,
                    'error': f"Error en anuncios: {ads_result['error']}",
                    'results': results
                }
            
            print("\n🔑 PASO 3: Insertando palabras clave...")
            keywords_result = self.insert_keywords(keywords_data)
            results['keywords'] = keywords_result
            
            if not keywords_result['success']:
                return {
                    'success': False,
                    'error': f"Error en palabras clave: {keywords_result['error']}",
                    'results': results
                }
            
            # 4. Resumen final
            total_inserted = (
                campaigns_result.get('inserted_count', 0) +
                ads_result.get('inserted_count', 0) +
                keywords_result.get('inserted_count', 0)
            )
            
            print("\n✅ INSERCIÓN COMPLETA EXITOSA!")
            print(f"📊 Total de registros insertados: {total_inserted}")
            
            return {
                'success': True,
                'message': f'Todos los datos insertados exitosamente. Total: {total_inserted} registros',
                'total_inserted': total_inserted,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en inserción completa: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_sql_file(self, sql_file_path: str) -> List[Dict]:
        """Extrae datos de un archivo SQL INSERT y los convierte a diccionarios"""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer las sentencias INSERT
            import re
            
            # Patrón para extraer INSERT statements
            pattern = r'INSERT INTO [^(]+\(([^)]+)\) VALUES \(([^;]+)\);'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not matches:
                print(f"⚠️ No se encontraron INSERT statements en {sql_file_path}")
                return []
            
            # Extraer columnas del primer match
            columns = [col.strip() for col in matches[0][0].split(',')]
            
            data_list = []
            for match in matches:
                values_str = match[1]
                # Parsear valores (esto es básico, puede necesitar mejoras para casos complejos)
                values = self._parse_sql_values(values_str)
                
                if len(values) == len(columns):
                    row_dict = dict(zip(columns, values))
                    data_list.append(row_dict)
            
            print(f"📄 {sql_file_path}: {len(data_list)} registros extraídos")
            return data_list
            
        except Exception as e:
            print(f"❌ Error parseando {sql_file_path}: {str(e)}")
            return []
    
    def _parse_sql_values(self, values_str: str) -> List:
        """Parsea una cadena de valores SQL y los convierte a tipos Python"""
        # Implementación básica - puede necesitar mejoras para casos complejos
        values = []
        current_value = ""
        in_quotes = False
        
        i = 0
        while i < len(values_str):
            char = values_str[i]
            
            if char == "'" and (i == 0 or values_str[i-1] != "\\"):
                in_quotes = not in_quotes
                current_value += char
            elif char == "," and not in_quotes:
                values.append(self._convert_sql_value(current_value.strip()))
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        # Agregar el último valor
        if current_value.strip():
            values.append(self._convert_sql_value(current_value.strip()))
        
        return values
    
    def _convert_sql_value(self, sql_value: str):
        """Convierte un valor SQL a tipo Python"""
        sql_value = sql_value.strip()
        
        if sql_value.upper() == 'NULL':
            return None
        elif sql_value.startswith("'") and sql_value.endswith("'"):
            # String value - remover comillas y unescape
            return sql_value[1:-1].replace("''", "'")
        else:
            # Número
            try:
                if '.' in sql_value:
                    return float(sql_value)
                else:
                    return int(sql_value)
            except ValueError:
                return sql_value
    
    def _clean_data_for_supabase(self, data: Dict) -> Dict:
        """Limpia los datos para inserción en Supabase"""
        clean_data = {}
        
        for key, value in data.items():
            # Remover espacios de las claves
            clean_key = key.strip()
            
            # Convertir valores vacíos a None
            if value == '' or value == 'NULL':
                clean_data[clean_key] = None
            else:
                clean_data[clean_key] = value
        
        return clean_data

def test_supabase_connection():
    """Función de prueba para verificar la conexión a Supabase"""
    try:
        client = SupabaseGoogleAdsClient()
        result = client.test_connection()
        
        if result['success']:
            print("✅ Conexión a Supabase exitosa!")
        else:
            print(f"❌ Error de conexión: {result['error']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error inicializando cliente: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    test_supabase_connection()
