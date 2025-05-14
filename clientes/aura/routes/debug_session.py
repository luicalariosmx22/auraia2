# ✅ Archivo: clientes/aura/routes/debug_session.py
from flask import Blueprint, current_app, jsonify, session

debug_session_bp = Blueprint("debug_session_bp", __name__, url_prefix="/debug")

@debug_session_bp.route("/session", methods=["GET"])
def debug_session():
    return jsonify({
        "session_interface": str(current_app.session_interface),
        "session_cookie_name": current_app.config.get("SESSION_COOKIE_NAME"),
        "session_contents": dict(session) if session else "vacía",
        "secret_key_present": bool(current_app.secret_key),
    })
