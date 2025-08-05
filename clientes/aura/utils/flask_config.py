from flask import Flask

def configure_flask_app(app: Flask):
    """Configura la aplicación Flask con los ajustes necesarios"""
    
    # Configuraciones básicas
    app.config.update(
        JSON_AS_ASCII=False,
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=False,
        JSONIFY_MIMETYPE='application/json; charset=utf-8'
    )
    
    # Configurar respuestas JSON
    @app.after_request
    def after_request(response):
        if response.mimetype == 'application/json':
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    return app
