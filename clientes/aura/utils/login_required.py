from functools import wraps
from flask import session, redirect

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("email"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("email") or not session.get("nombre_nora"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
