from flask import Blueprint

my_blueprint = Blueprint('my_blueprint', __name__)

@my_blueprint.route('/ruta-no-definida')
def ruta_no_definida():
    return "¡Hola, esta es la ruta no definida!"