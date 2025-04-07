from routes.main import main_bp
from app import app, socketio

# Ya está registrado en app.py, no necesitas hacer más
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    socketio.run(app,
                 host="0.0.0.0",
                 port=port,
                 debug=debug,
                 use_reloader=debug,
                 allow_unsafe_werkzeug=debug)
