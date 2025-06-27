from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import traceback
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Importar cliente de Supabase
try:
    from supabase_client import SupabaseGoogleAdsClient
    SUPABASE_AVAILABLE = True
    print("✅ Cliente de Supabase disponible")
except ImportError as e:
    SUPABASE_AVAILABLE = False
    print(f"⚠️ Cliente de Supabase no disponible: {e}")

app = Flask(__name__)
app.secret_key = 'google_ads_sql_generator_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('outputs', exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal"""
    has_openai_key = bool(os.getenv('OPENAI_API_KEY'))
    return render_template('index.html', has_openai_key=has_openai_key)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Maneja la subida y procesamiento de archivos Excel"""
    try:
        print("=== DEBUG UPLOAD ===")
        print(f"Request files: {request.files}")
        print(f"Request form: {request.form}")
        print(f"Request content type: {request.content_type}")
        
        # Verificar si se subió un archivo
        if 'file' not in request.files:
            print("ERROR: 'file' no está en request.files")
            return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'})
        
        file = request.files['file']
        print(f"File object: {file}")
        print(f"File filename: '{file.filename}'")
        print(f"File content type: {file.content_type}")
        
        if file.filename == '':
            print("ERROR: filename está vacío")
            return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'})
        
        if not allowed_file(file.filename):
            print(f"ERROR: Archivo no permitido: {file.filename}")
            return jsonify({'success': False, 'error': 'Formato de archivo no válido. Use .xlsx o .xls'})
        
        # Obtener parámetros
        generator_type = request.form.get('generator_type', 'simple')
        table_type = request.form.get('table_type', 'anuncios')
        sheet_name = request.form.get('sheet_name', '').strip()
        if not sheet_name:
            sheet_name = None
        
        print(f"Generator type: {generator_type}")
        print(f"Table type: {table_type}")
        print(f"Sheet name: {sheet_name}")
        
        # Guardar archivo subido
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"Guardando archivo en: {filepath}")
        file.save(filepath)
        print(f"Archivo guardado exitosamente. Tamaño: {os.path.getsize(filepath)} bytes")
        
        # Procesar según el tipo de generador
        print(f"Iniciando procesamiento con generador: {generator_type}, tabla: {table_type}")
        if generator_type == 'ai' and os.getenv('OPENAI_API_KEY'):
            print("Usando generador con IA")
            result = process_with_ai(filepath, sheet_name, table_type)
        else:
            print("Usando generador simple")
            result = process_simple(filepath, sheet_name, table_type)
        
        print(f"Resultado del procesamiento: {result}")
        
        # Limpiar archivo temporal
        try:
            os.remove(filepath)
            print(f"Archivo temporal eliminado: {filepath}")
        except Exception as e:
            print(f"Error eliminando archivo temporal: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR GENERAL en upload_file: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'error': f'Error procesando archivo: {str(e)}',
            'traceback': traceback.format_exc()
        })

def process_with_ai(filepath, sheet_name=None, table_type='anuncios'):
    """Procesa el archivo usando IA"""
    try:
        from google_ads_sql_generator import GoogleAdsExcelAnalyzer
        
        analyzer = GoogleAdsExcelAnalyzer()
        if table_type == 'anuncios':
            table_suffix = "anuncios"
        elif table_type == 'palabras_clave':
            table_suffix = "palabras_clave"
        else:  # campañas
            table_suffix = "campañas"
        
        output_file = f"outputs/google_ads_ai_{table_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        result = analyzer.process_excel_to_sql(filepath, output_file, sheet_name, table_type)
        
        if result['success']:
            # Leer primeras líneas del archivo para preview
            preview_lines = []
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    preview_lines = f.readlines()[:10]
            except:
                preview_lines = ["Error al leer el archivo generado"]
            
            return {
                'success': True,
                'message': f'Archivo procesado exitosamente con IA (tabla: {table_type})',
                'total_records': result['total_records'],
                'output_file': output_file,
                'preview': ''.join(preview_lines),
                'analysis': result.get('analysis', {}),
                'generator_type': 'ai',
                'table_type': table_type
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error en procesamiento con IA: {str(e)}'
        }

def process_simple(filepath, sheet_name=None, table_type='anuncios'):
    """Procesa el archivo con mapeo simple"""
    try:
        print(f"=== PROCESS_SIMPLE DEBUG ===")
        print(f"Filepath: {filepath}")
        print(f"Sheet name: {sheet_name}")
        print(f"Table type: {table_type}")
        print(f"Archivo existe: {os.path.exists(filepath)}")
        
        from simple_excel_to_sql import SimpleExcelToSQL
        
        converter = SimpleExcelToSQL()
        if table_type == 'anuncios':
            table_suffix = "anuncios"
        elif table_type == 'palabras_clave':
            table_suffix = "palabras_clave"
        else:  # campañas
            table_suffix = "campañas"
        
        output_file = f"outputs/google_ads_simple_{table_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        print(f"Output file: {output_file}")
        print("Iniciando procesamiento...")
        
        success = converter.process_excel_simple(filepath, output_file, sheet_name, table_type)
        
        print(f"Procesamiento completado. Success: {success}")
        
        if success:
            # Contar líneas SQL para estimar registros
            sql_count = 0
            preview_lines = []
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    sql_count = sum(1 for line in lines if line.strip().startswith('INSERT'))
                    preview_lines = lines[:10]
                print(f"SQL generado. Líneas INSERT: {sql_count}")
            except Exception as e:
                print(f"Error leyendo archivo de salida: {e}")
                preview_lines = ["Error al leer el archivo generado"]
            
            result = {
                'success': True,
                'message': f'Archivo procesado exitosamente con mapeo simple (tabla: {table_type})',
                'total_records': sql_count,
                'output_file': output_file,
                'preview': ''.join(preview_lines),
                'generator_type': 'simple',
                'table_type': table_type
            }
            print(f"Resultado final: {result}")
            return result
        else:
            return {
                'success': False,
                'error': 'Error en el procesamiento simple'
            }
            
    except Exception as e:
        print(f"ERROR en process_simple: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': f'Error en procesamiento simple: {str(e)}'
        }

@app.route('/download/<path:filename>')
def download_file(filename):
    """Descarga el archivo SQL generado"""
    try:
        return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))
    except Exception as e:
        flash(f'Error al descargar archivo: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/preview/<path:filename>')
def preview_file(filename):
    """Muestra una vista previa del archivo SQL"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return render_template('preview.html', 
                             filename=os.path.basename(filename),
                             content=content,
                             line_count=len(content.split('\n')))
    except Exception as e:
        flash(f'Error al mostrar vista previa: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/test')
def test_generators():
    """Página de testing"""
    return render_template('test.html')

@app.route('/run_test', methods=['POST'])
def run_test():
    """Ejecuta los tests"""
    try:
        from test_generators import create_sample_excel, SimpleExcelToSQL
        
        # Crear archivo de ejemplo
        excel_file = create_sample_excel()
        
        # Probar generador simple
        converter = SimpleExcelToSQL()
        output_file = f"outputs/test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        success = converter.process_excel_simple(excel_file, output_file)
        
        if success:
            # Leer resultado
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limpiar archivo de ejemplo
            try:
                os.remove(excel_file)
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': 'Test ejecutado exitosamente',
                'output_file': output_file,
                'preview': content[:2000] + "..." if len(content) > 2000 else content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error en la ejecución del test'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error ejecutando test: {str(e)}'
        })

@app.route('/api/config')
def get_config():
    """Retorna configuración de la aplicación"""
    has_supabase = bool(os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_ANON_KEY'))
    return jsonify({
        'has_openai_key': bool(os.getenv('OPENAI_API_KEY')),
        'has_supabase_config': has_supabase,
        'supabase_available': SUPABASE_AVAILABLE and has_supabase,
        'max_file_size': app.config['MAX_CONTENT_LENGTH'],
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

@app.route('/api/supabase/test', methods=['POST'])
def test_supabase_connection():
    """Prueba la conexión a Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Cliente de Supabase no disponible. Instala: pip install supabase'
            })
        
        client = SupabaseGoogleAdsClient()
        result = client.test_connection()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error probando conexión a Supabase: {str(e)}'
        })

@app.route('/api/supabase/insert', methods=['POST'])
def insert_to_supabase():
    """Inserta los datos procesados a Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Cliente de Supabase no disponible'
            })
        
        data = request.get_json()
        
        # Verificar que se enviaron los archivos necesarios
        required_files = ['campaigns_file', 'ads_file', 'keywords_file']
        for file_key in required_files:
            if file_key not in data:
                return jsonify({
                    'success': False,
                    'error': f'Archivo requerido no encontrado: {file_key}'
                })
        
        # Verificar que los archivos existen
        for file_key in required_files:
            file_path = data[file_key]
            if not os.path.exists(file_path):
                return jsonify({
                    'success': False,
                    'error': f'Archivo no encontrado: {file_path}'
                })
        
        # Inicializar cliente de Supabase
        client = SupabaseGoogleAdsClient()
        
        # Insertar todos los datos
        clear_tables = data.get('clear_tables', True)
        result = client.insert_all_data(
            campaigns_file=data['campaigns_file'],
            ads_file=data['ads_file'],
            keywords_file=data['keywords_file'],
            clear_tables=clear_tables
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error insertando a Supabase: {str(e)}'
        })

@app.route('/api/supabase/clear', methods=['POST'])
def clear_supabase_tables():
    """Limpia todas las tablas de Google Ads en Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Cliente de Supabase no disponible'
            })
        
        client = SupabaseGoogleAdsClient()
        result = client.clear_all_tables()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error limpiando tablas: {str(e)}'
        })

@app.route('/api/file-info/<path:filename>')
def get_file_info(filename):
    """Obtiene información sobre un archivo SQL procesado"""
    try:
        if not os.path.exists(filename):
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado'
            })
        
        # Leer primeras líneas para análisis
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Contar INSERT statements
        insert_count = sum(1 for line in lines if line.strip().startswith('INSERT'))
        
        # Obtener información del archivo
        file_stats = os.stat(filename)
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(filename),
            'size_bytes': file_stats.st_size,
            'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
            'insert_count': insert_count,
            'total_lines': len(lines),
            'preview': ''.join(lines[:5])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo información del archivo: {str(e)}'
        })

@app.route('/test-button')
def test_button():
    """Página de prueba para verificar el botón de limpiar tablas"""
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Test Button</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>🧪 Test del Botón Limpiar Tablas</h2>
            <div class="row mt-4">
                <div class="col-md-3">
                    <button class="btn btn-warning w-100">
                        <i class="fas fa-cogs"></i> Procesar
                    </button>
                </div>
                <div class="col-md-3">
                    <button class="btn btn-outline-info w-100">
                        <i class="fas fa-download"></i> Descargar
                    </button>
                </div>
                <div class="col-md-3">
                    <button class="btn btn-success w-100">
                        <i class="fas fa-database"></i> Insertar
                    </button>
                </div>
                <div class="col-md-3">
                    <button class="btn btn-outline-danger w-100" onclick="testClear()">
                        <i class="fas fa-trash-alt"></i> Limpiar Tablas
                    </button>
                </div>
            </div>
            <div class="mt-3">
                <p>Si ves 4 botones arriba (incluyendo uno rojo "Limpiar Tablas"), entonces el botón está funcionando.</p>
                <a href="/" class="btn btn-primary">Volver a la aplicación principal</a>
            </div>
        </div>
        <script>
            function testClear() {
                if (confirm('¿Confirmas que quieres probar la funcionalidad de limpiar tablas?')) {
                    fetch('/api/supabase/clear', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert('Resultado: ' + JSON.stringify(data, null, 2));
                    })
                    .catch(e => alert('Error: ' + e.message));
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/supabase/preview_data', methods=['GET'])
def preview_google_ads_data():
    """Vista previa de datos en las tablas de Google Ads"""
    try:
        if not SUPABASE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Cliente de Supabase no disponible'
            })
        
        client = SupabaseGoogleAdsClient()
        
        # Obtener datos de cada tabla
        campañas = client.supabase.table('google_ads_campañas').select('*').execute()
        anuncios = client.supabase.table('google_ads_reporte_anuncios').select('*').execute()
        keywords = client.supabase.table('google_ads_palabras_clave').select('*').execute()
        
        return jsonify({
            'success': True,
            'data': {
                'campañas': campañas.data,
                'anuncios': anuncios.data,
                'keywords': keywords.data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo datos: {str(e)}'
        })

@app.route('/clear_tables', methods=['POST'])
def clear_tables_endpoint():
    """Endpoint alternativo para limpiar todas las tablas de Google Ads"""
    return clear_supabase_tables()

if __name__ == '__main__':
    print("🚀 Iniciando Google Ads SQL Generator Web")
    print("🌐 Servidor disponible en: http://localhost:5001")
    print("📁 Archivos de salida en: ./outputs/")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
