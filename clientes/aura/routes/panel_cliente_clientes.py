from flask import Blueprint, render_template, session, redirect, url_for
from utils.validar_modulo_activo import modulo_activo_para_nora

panel_cliente_clientes_bp = Blueprint('panel_cliente_clientes_bp', __name__)

@panel_cliente_clientes_bp.route('/panel_cliente/<nombre_nora>/clientes')
def vista_clientes(nombre_nora):
    if not session.get("user"):
        return redirect(url_for('login_bp.login'))

    if not modulo_activo_para_nora(nombre_nora, 'clientes'):
        return "Módulo no activo", 403

    return render_template('panel_cliente_clientes/index.html', nombre_nora=nombre_nora, user=session.get("user"))
