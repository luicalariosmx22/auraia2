from flask import Blueprint, request, jsonify
from clientes.aura.utils.supabase_client import supabase

process_message_bp = Blueprint('process_message', __name__)

@process_message_bp.route('/process_message', methods=['POST'])
def process_message():
    data = request.get_json()
    print("🟢 [process_message.py] Payload recibido:", data)  # Log para depuración
    user_id = data.get('user_id')
    message = data.get('message')

    # Process the message and interact with Supabase
    response = supabase.table('messages').insert({
        'user_id': user_id,
        'message': message
    }).execute()

    print("🟢 [process_message.py] Respuesta de supabase:", response)  # Log para depuración
    return jsonify({'status': 'success', 'data': response})