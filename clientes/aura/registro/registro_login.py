from flask import Blueprint, request, render_template, redirect, url_for

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/google", methods=["GET", "POST"])
def login_google():
    print("DEBUG: Entrando a login_google")
    if request.method == "GET":
        print("DEBUG: Método GET")
        return render_template("login_google.html")
    elif request.method == "POST":
        print("DEBUG: Método POST")
        return redirect(url_for("home"))
    else:
        print("DEBUG: Método no soportado")
        return "Método no soportado", 405

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp, url_prefix="/login")
