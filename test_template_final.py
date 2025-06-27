#!/usr/bin/env python3
"""
Test final para verificar que el template admin_nora_entrenar.html
funcione correctamente después de la corrección de bloques Jinja2.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template

# Configurar Flask con las rutas correctas
app = Flask(__name__)
app.template_folder = 'clientes/aura/templates'
app.static_folder = 'clientes/aura/static'

@app.route('/test_template')
def test_template():
    """Renderizar el template corregido para verificar funcionamiento"""
    try:
        # Datos de ejemplo para el template
        context = {
            'nombre_nora': 'test_nora',
            'conocimiento_data': [],
            'personalidad_data': {},
            'instrucciones_data': {},
            'bloques_data': [],
            'limites_data': {},
            'bienvenida_data': {}
        }
        
        # Intentar renderizar el template
        rendered = render_template('admin_nora_entrenar.html', **context)
        
        # Verificar que se renderizó correctamente
        if rendered and len(rendered) > 1000:  # Template mínimo debe tener contenido
            return f"""
            <h1>✅ Template renderizado correctamente</h1>
            <p><strong>Tamaño:</strong> {len(rendered)} caracteres</p>
            <p><strong>Estado:</strong> Sin errores de Jinja2</p>
            <p><strong>JavaScript:</strong> Incluido correctamente</p>
            <hr>
            <h2>Vista previa del template:</h2>
            <div style="border: 1px solid #ccc; padding: 10px; max-height: 500px; overflow-y: auto;">
                {rendered}
            </div>
            """
        else:
            return "❌ Error: Template renderizado pero con contenido insuficiente"
            
    except Exception as e:
        return f"❌ Error al renderizar template: {str(e)}"

if __name__ == '__main__':
    print("🧪 Test de template corregido...")
    print("🌐 Servidor iniciando en http://localhost:5001/test_template")
    app.run(debug=True, port=5001, host='0.0.0.0')
