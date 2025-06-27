from flask import session, redirect, url_for, request
from functools import wraps

def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("email"):
            return redirect(url_for("simple_login.login_simple"))
        return func(*args, **kwargs)
    return wrapper
