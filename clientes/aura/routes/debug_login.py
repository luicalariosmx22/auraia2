# clientes/aura/routes/debug_login.py
from flask import Blueprint, session, jsonify

debug_login_bp = Blueprint("debug_login", __name__)

@debug_login_bp.route("/debug/login_info")
def login_info():
    if "user" in session:
        return jsonify({
            "logged_in": True,
            "name": session.get("name"),
            "email": session.get("email"),
            "is_admin": session.get("is_admin", False)
        })
    else:
        return jsonify({
            "logged_in": False,
            "message": "Ningún usuario está logueado actualmente."
        })
