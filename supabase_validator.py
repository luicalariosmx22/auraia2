import os
import re
from supabase import create_client
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional

# Configuración
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
REPO_ROUTES_PATH = "clientes/aura/routes"

class SupabaseTableChecker:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.verified_tables = set()  # Tablas que sabemos que existen
        self.results = []

    def check_table_exists(self, table_name: str) -> bool:
        """Verifica si una tabla existe intentando acceder a ella"""
        if table_name in self.verified_tables:
            return True

        try:
            # Intenta obtener un solo registro
            response = self.supabase.from_(table_name).select("*").limit(1).execute()
            if not hasattr(response, 'data'):
                return False

            self.verified_tables.add(table_name)
            return True
        except:
            return False

    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Verifica si una columna existe en una tabla sin depender de si hay datos."""
        if not self.check_table_exists(table_name):
            return False

        try:
            # Solo comprobar si la consulta es válida, no si hay datos
            self.supabase.from_(table_name).select(column_name).limit(1).execute()
            return True
        except Exception as e:
            print(f"⚠️ Error al verificar columna '{column_name}' en tabla '{table_name}': {e}")
            return False
    
    def analyze_routes(self, repo_path: str):
        """Analiza todos los archivos en la carpeta de routes"""
        routes_dir = os.path.join(repo_path, REPO_ROUTES_PATH)
        
        if not os.path.exists(routes_dir):
            print(f"Error: No se encontró la carpeta {routes_dir}")
            return False
        
        print(f"\nAnalizando archivos en {routes_dir}...")
        
        for filename in os.listdir(routes_dir):
            if not filename.endswith('.py'):
                continue
                
            filepath = os.path.join(routes_dir, filename)
            self._analyze_file(filepath)
        
        return True
    
    def _analyze_file(self, filepath: str):
        """Analiza un archivo individual"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Buscar todas las funciones en el archivo
            functions = self._extract_functions(content)
            
            for func_name, func_code in functions.items():
                # Buscar consultas a Supabase en esta función
                queries = self._find_supabase_queries(func_code)
                
                for query in queries:
                    # Verificar contra la base de datos real
                    table_exists = self.check_table_exists(query['table'])
                    columns_exist = []
                    conditions_exist = []
                    
                    for col in query['columns']:
                        if col != '*':
                            col_exists = self.check_column_exists(query['table'], col)
                            columns_exist.append(col_exists)
                            if not col_exists:
                                print(f"⚠️ Columna '{col}' no encontrada en tabla '{query['table']}' en archivo '{filepath}', función '{func_name}'")
                    
                    for col, _ in query['conditions']:
                        cond_exists = self.check_column_exists(query['table'], col)
                        conditions_exist.append(cond_exists)
                        if not cond_exists:
                            print(f"⚠️ Condición con columna '{col}' no encontrada en tabla '{query['table']}' en archivo '{filepath}', función '{func_name}'")
                    
                    self.results.append({
                        'file': os.path.basename(filepath),
                        'function': func_name,
                        'table': query['table'],
                        'table_exists': table_exists,
                        'columns': query['columns'],
                        'columns_exist': columns_exist,
                        'conditions': query['conditions'],
                        'conditions_exist': conditions_exist
                    })
    
    def _extract_functions(self, content: str) -> Dict[str, str]:
        """Extrae todas las funciones del archivo"""
        functions = {}
        pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:\s*\n((?:\s+.+\n)+)'
        
        for match in re.finditer(pattern, content):
            func_name = match.group(1)
            func_code = match.group(2)
            functions[func_name] = func_code
        
        return functions
    
    def _find_supabase_queries(self, code: str) -> List[Dict]:
        """Encuentra consultas a Supabase en el código"""
        queries = []
        pattern = r'supabase\.(?:from_|table)\([\'"](.+?)[\'"]\)\s*\.select\([\'"](.+?)[\'"]\)([\s\S]*?)\.execute\(\)'
        
        for match in re.finditer(pattern, code):
            table = match.group(1)
            columns = [col.strip() for col in match.group(2).split(',') if col.strip()]
            conditions = self._extract_conditions(match.group(3))
            
            queries.append({
                'table': table,
                'columns': columns,
                'conditions': conditions
            })
        
        return queries
    
    def _extract_conditions(self, code: str) -> List[Tuple[str, str]]:
        """Extrae condiciones (.eq, .gt, etc.)"""
        conditions = []
        pattern = r'\.(eq|neq|gt|lt|gte|lte|like|ilike)\([\'"](.+?)[\'"]\s*,\s*[\'"]?(.+?)[\'"]?\)'
        
        for match in re.finditer(pattern, code):
            operator = match.group(1)
            column = match.group(2)
            conditions.append((column, operator))
        
        return conditions
    
    def generate_report(self, output_file: str = "supabase_validation_report.txt"):
        """Genera un reporte detallado"""
        report = []
        
        if not self.results:
            report.append("No se encontraron consultas a Supabase en los archivos analizados.")
        else:
            report.append("=== VERIFICACIÓN DE TABLAS Y CAMPOS EN SUPABASE ===")
            report.append("Se verificó cada consulta contra la base de datos real\n")
            
            current_file = None
            for item in sorted(self.results, key=lambda x: (x['file'], x['function'])):
                if item['file'] != current_file:
                    current_file = item['file']
                    report.append(f"\n📄 ARCHIVO: {current_file}")
                
                report.append(f"\n🔹 Función: {item['function']}()")
                report.append(f"   Tabla: {item['table']} {'✅' if item['table_exists'] else '❌ (No existe)'}")
                
                if not item['table_exists']:
                    continue
                
                if item['columns']:
                    cols_status = []
                    for col, exists in zip(item['columns'], item['columns_exist']):
                        if col == '*':
                            cols_status.append(f"{col}✅")
                        else:
                            cols_status.append(f"{col}{'✅' if exists else '❌'}")
                    report.append(f"   Columnas: {', '.join(cols_status)}")
                
                if item['conditions']:
                    conds_status = []
                    for (col, op), exists in zip(item['conditions'], item['conditions_exist']):
                        conds_status.append(f"{col} {op.upper()}{'✅' if exists else '❌'}")
                    report.append(f"   Condiciones: {' | '.join(conds_status)}")
                
                # Resumen de problemas
                missing_cols = [col for col, exists in zip(item['columns'], item['columns_exist']) 
                              if col != '*' and not exists]
                missing_conds = [col for (col, _), exists in zip(item['conditions'], item['conditions_exist']) 
                               if not exists]
                
                if missing_cols or missing_conds:
                    report.append(f"   ⚠️ Problemas encontrados:")
                    if missing_cols:
                        report.append(f"     - Columnas faltantes: {', '.join(missing_cols)}")
                    if missing_conds:
                        report.append(f"     - Campos en condiciones faltantes: {', '.join(missing_conds)}")
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        
        print(f"\nReporte generado en: {output_file}")

if __name__ == '__main__':
    checker = SupabaseTableChecker()
    
    try:
        # Paso 1: Analizar archivos de routes
        repo_path = input("Ingrese la ruta completa al repositorio AuraAI2: ").strip('"')
        if not checker.analyze_routes(repo_path):
            exit(1)
        
        # Paso 2: Generar reporte
        checker.generate_report()
        
    except Exception as e:
        print(f"\nError durante la ejecución: {str(e)}")