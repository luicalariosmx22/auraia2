from flask import Blueprint, request, redirect, url_for, flash
from clientes.aura.utils.supabase_client import supabase

panel_cliente_pagos_recibo = Blueprint('panel_cliente_pagos_recibo', __name__)

@panel_cliente_pagos_recibo.route('/eliminar/<nombre_nora>/<int:pago_id>', methods=['POST'])
def eliminar_recibo(nombre_nora, pago_id):
    """
    Elimina un recibo/pago por su ID y redirige al listado de pagos.
    """
    supabase.table('pagos').delete().eq('id', pago_id).execute()
    flash('Recibo eliminado correctamente.', 'success')
    return redirect(url_for('panel_cliente_pagos.index', nombre_nora=nombre_nora))