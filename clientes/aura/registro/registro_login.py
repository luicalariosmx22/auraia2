import os
from flask import Blueprint, request, redirect, url_for, render_template
from clientes.aura.auth.login import login_bp

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp, url_prefix="")
