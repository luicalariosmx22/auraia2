# app.py
import os
from clientes.aura import create_app
import sys
import time
from flask import send_file

# Create the Flask application
app = create_app()

# This makes the app available for Gunicorn and other WSGI servers
application = app  # For WSGI servers that expect 'application' variable

# Ruta de prueba para servir el archivo de test
@app.route('/test_importacion_google_ads.html')
def test_importacion():
    return send_file('test_importacion_google_ads.html')

# Ruta de prueba para el test simple
@app.route('/test_simple_insert.html')
def test_simple_insert():
    return send_file('test_simple_insert.html')

# =====================================
# 🔍 DEBUG: Ruta temporal para verificar el problema - SOLO localhost
# =====================================
@app.route('/debug_rutas')
def debug_rutas():
    from flask import request, jsonify
    
    # Solo permitir en localhost
    if not request.host.lower().startswith(('localhost:', '127.0.0.1:', '0.0.0.0:')):
        return jsonify({"error": "Acceso denegado"}), 403
    
    rutas = []
    for rule in app.url_map.iter_rules():
        if rule.rule == '/':
            rutas.append({
                'ruta': rule.rule,
                'endpoint': rule.endpoint,
                'metodos': list(rule.methods),
                'blueprint': rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'app_level'
            })
    return f"<pre>{rutas}</pre>"

if __name__ == '__main__':
    # For local development with Flask's built-in server
    print("🚀 Starting NORA application in development mode...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    # For production with WSGI servers like Gunicorn
    print("🚀 NORA application ready for WSGI server...")
    # Remove the gunicorn.run() call that was causing issues
    pass