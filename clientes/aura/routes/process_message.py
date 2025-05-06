from flask import Blueprint, request, jsonify
from clientes.aura.utils import supabase_client as supabase

process_message_bp = Blueprint('process_message', __name__)

@process_message_bp.route('/process_message', methods=['POST'])
def process_message():
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    # Process the message and interact with Supabase
    response = supabase.table('messages').insert({
        'user_id': user_id,
        'message': message
    }).execute()

    return jsonify({'status': 'success', 'data': response})